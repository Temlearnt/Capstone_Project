import { JOB_DESCRIPTIONS } from '../data/candidates';
import { apiRequest, isMockApi } from './apiClient';
import { getStatusFromScore } from '../utils/helpers';

const COLORS = [
  ['#8b5cf6', 'rgba(139,92,246,0.12)'],
  ['#34d399', 'rgba(52,211,153,0.12)'],
  ['#60a5fa', 'rgba(96,165,250,0.12)'],
  ['#f472b6', 'rgba(244,114,182,0.12)'],
  ['#fb923c', 'rgba(251,146,60,0.12)'],
];

let latestScreeningId = null;

function sleep(ms) {
  return new Promise(resolve => window.setTimeout(resolve, ms));
}

function initials(name = 'Kandidat') {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map(word => word[0]?.toUpperCase())
    .join('') || 'K';
}

function extractScreeningId(payload) {
  return (
    payload?.screening_id ||
    payload?.id ||
    payload?.data?.screening_id ||
    payload?.data?.id ||
    payload?.result?.screening_id ||
    null
  );
}

function extractCandidateList(payload) {
  if (Array.isArray(payload)) return payload;

  const candidates =
    payload?.candidates ||
    payload?.data?.candidates ||
    payload?.data?.results ||
    payload?.data?.rankings ||
    payload?.results ||
    payload?.rankings ||
    payload?.history ||
    payload?.items ||
    [];

  if (Array.isArray(candidates)) return candidates;
  if (candidates && typeof candidates === 'object') return Object.values(candidates);
  return [];
}

function extractScreeningList(payload) {
  const screenings = payload?.screenings || payload?.data?.screenings || payload?.sessions || payload?.data?.sessions || [];
  if (Array.isArray(screenings)) return screenings;
  if (screenings && typeof screenings === 'object') return Object.values(screenings);
  return [];
}

function decorateBatch(candidate, screening, index) {
  const screeningId = screening?.screening_id || screening?.id || candidate?.screening_id || candidate?.screeningId;
  const createdAt = screening?.created_at || candidate?.created_at || candidate?.uploaded_at || '';
  const batchNumber = index + 1;
  const labelDate = createdAt ? ` - ${String(createdAt).slice(0, 10)}` : '';
  return {
    ...candidate,
    screening_id: screeningId,
    batch_id: candidate?.batch_id || candidate?.batchId || screeningId || `batch-${batchNumber}`,
    batch_label: candidate?.batch_label || candidate?.batchLabel || `Batch ${batchNumber}${labelDate}`,
    uploaded_at: candidate?.uploaded_at || candidate?.uploadedAt || createdAt,
  };
}

function isScreeningComplete(payload) {
  const status = String(payload?.status || payload?.data?.status || '').toLowerCase();
  return ['completed', 'complete', 'done', 'finished', 'success', 'selesai'].includes(status);
}

export function normalizeCandidate(candidate, index = 0) {
  const raw = candidate?.candidate || candidate?.data || candidate || {};
  const score = Number(raw.score ?? raw.total ?? raw.match_score ?? raw.final_score ?? raw.overall_score ?? 0);
  const [colorAccent, colorBg] = COLORS[index % COLORS.length];

  return {
    id: raw.id || raw.candidate_id || raw.email || `${raw.name || raw.full_name || 'candidate'}-${index}`,
    name: raw.name || raw.full_name || raw.candidate_name || raw.filename || 'Kandidat Baru',
    initials: raw.initials || initials(raw.name || raw.full_name || raw.candidate_name),
    colorAccent: raw.colorAccent || colorAccent,
    colorBg: raw.colorBg || colorBg,
    email: raw.email || '-',
    phone: raw.phone || raw.phone_number || raw.telepon || '-',
    location: raw.location || raw.alamat || '-',
    position: raw.position || raw.role || raw.applied_role || raw.job_title || 'Kandidat',
    score,
    status: raw.status || getStatusFromScore(score),
    education: {
      level: raw.education?.level || raw.education_level || raw.pendidikan?.level || '-',
      major: raw.education?.major || raw.major || raw.jurusan || '-',
      university: raw.education?.university || raw.university || raw.universitas || '-',
      gpa: raw.education?.gpa || raw.gpa || raw.ipk || '-',
      year: raw.education?.year || raw.education_year || raw.tahun_lulus || '-',
    },
    experience: {
      years: Number(raw.experience?.years ?? raw.experience_years ?? raw.years_experience ?? 0),
      label: raw.experience?.label || raw.experience_label || `${raw.experience?.years ?? raw.experience_years ?? raw.years_experience ?? 0} tahun`,
    },
    skills: Array.isArray(raw.skills) ? raw.skills : String(raw.skills || '').split(',').map(s => s.trim()).filter(Boolean),
    scoreBreakdown: raw.scoreBreakdown || raw.score_breakdown || {
      skill: raw.skill_score ?? score,
      experience: raw.experience_score ?? score,
      education: raw.education_score ?? score,
      relevance: raw.relevance_score ?? score,
    },
    workHistory: raw.workHistory || raw.work_history || raw.experience?.jobs || [],
    cvText: raw.cvText || raw.cv_text || raw.summary || raw.ringkasan || 'Ringkasan CV akan muncul setelah backend screening mengirim data.',
    batchId: raw.batch_id || raw.batchId || raw.screening_id || raw.screeningId || raw.upload_id || raw.uploadId || raw.created_at || raw.uploaded_at || 'batch-terbaru',
    batchLabel: raw.batch_label || raw.batchLabel || raw.batch_name || raw.batchName || (raw.screening_id || raw.screeningId ? `Batch ${raw.screening_id || raw.screeningId}` : (raw.uploaded_at || raw.created_at ? `Upload ${String(raw.uploaded_at || raw.created_at).slice(0, 10)}` : 'Batch terbaru')),
    uploadedAt: raw.uploaded_at || raw.created_at || raw.uploadDate || raw.uploadedAt || '',
  };
}

async function requestFirstAvailable(paths, options) {
  let lastError;
  for (const path of paths) {
    try {
      return await apiRequest(path, options);
    } catch (err) {
      lastError = err;
      if (err?.status !== 404) break;
    }
  }
  throw lastError;
}

export async function getCandidates() {
  if (isMockApi()) return [];

  // Backend FastAPI saat ini menyimpan batch di /screen/history lalu hasil tiap batch di /screen/{id}/result.
  // Ini membuat upload lama tetap tampil dan upload baru hanya menambah batch baru.
  try {
    const historyPayload = await requestFirstAvailable(['/screen/history', '/dashboard/recent-screenings', '/history/']);
    const screenings = extractScreeningList(historyPayload);

    if (screenings.length) {
      const batches = await Promise.allSettled(
        screenings.map(async (screening, index) => {
          const screeningId = screening?.screening_id || screening?.id;
          if (!screeningId) return [];
          const resultPayload = await requestFirstAvailable([
            `/screen/${screeningId}/result`,
            `/result/${screeningId}`,
            `/dashboard/screening/${screeningId}`,
          ]);
          return extractCandidateList(resultPayload).map(candidate => decorateBatch(candidate, screening, index));
        })
      );

      return batches
        .flatMap(item => (item.status === 'fulfilled' ? item.value : []))
        .map(normalizeCandidate)
        .sort((a, b) => b.score - a.score);
    }

    const directList = extractCandidateList(historyPayload);
    return directList.map(normalizeCandidate).sort((a, b) => b.score - a.score);
  } catch {
    try {
      const payload = await requestFirstAvailable(['/dashboard/top-candidates', '/api/candidates']);
      return extractCandidateList(payload).map(normalizeCandidate).sort((a, b) => b.score - a.score);
    } catch {
      return [];
    }
  }
}

function normalizeJobRoles(payload) {
  const rawRoles = Array.isArray(payload)
    ? payload
    : (payload?.data || payload?.job_roles || payload?.roles || payload?.items || []);

  if (!Array.isArray(rawRoles) || rawRoles.length === 0) return JOB_DESCRIPTIONS;

  return rawRoles.reduce((acc, role) => {
    const name = role?.name || role?.role_name || role?.title;
    if (!name) return acc;

    const skills = Array.isArray(role?.default_skills)
      ? role.default_skills
      : String(role?.default_skills || role?.skills || '')
        .split(',')
        .map(item => item.trim())
        .filter(Boolean);

    const suggestedJd = role?.suggested_jd || role?.job_description || role?.description || '';
    const skillText = skills.length
      ? `\n\nSkill utama yang diharapkan:\n- ${skills.join('\n- ')}`
      : '';

    acc[name] = `${suggestedJd}${skillText}`.trim() || JOB_DESCRIPTIONS[name] || '';
    return acc;
  }, {});
}

export async function getJobDescriptions() {
  if (isMockApi()) return JOB_DESCRIPTIONS;

  try {
    const payload = await apiRequest('/job-roles/');
    const normalizedRoles = normalizeJobRoles(payload);
    return Object.keys(normalizedRoles).length ? normalizedRoles : JOB_DESCRIPTIONS;
  } catch {
    return JOB_DESCRIPTIONS;
  }
}

export async function uploadCVFiles({ files, role, jobDescription, weights }) {
  if (isMockApi()) {
    await sleep(900);
    throw new Error('URL API belum diisi. Isi VITE_API_URL atau REACT_APP_API_URL terlebih dahulu. Hubungkan frontend ke FastAPI terlebih dahulu.');
  }

  const formData = new FormData();
  files.forEach(item => {
    const file = item.file || item;
    formData.append('files', file);
  });
  formData.append('role', role);
  formData.append('job_description', jobDescription);
  if (weights) {
    formData.append('weights', JSON.stringify(weights));
    formData.append('skill_weight', String(weights.skill ?? 0));
    formData.append('education_weight', String(weights.education ?? 0));
    formData.append('experience_weight', String(weights.experience ?? 0));
  }

  const payload = await requestFirstAvailable(['/screen/', '/upload/', '/api/cv/upload'], {
    method: 'POST',
    body: formData,
  });

  latestScreeningId = extractScreeningId(payload) || latestScreeningId;
  return payload;
}

async function fetchScreeningResult(screeningId) {
  const paths = [
    `/screen/${screeningId}/result`,
    `/result/${screeningId}`,
    `/status/${screeningId}`,
    `/screen/${screeningId}/status`,
  ];
  const payload = await requestFirstAvailable(paths);
  latestScreeningId = extractScreeningId(payload) || screeningId;
  return payload;
}

async function waitForScreening(screeningId) {
  if (!screeningId) return null;

  for (let attempt = 0; attempt < 20; attempt += 1) {
    const statusPayload = await requestFirstAvailable([
      `/status/${screeningId}`,
      `/screen/${screeningId}/status`,
    ]);

    const list = extractCandidateList(statusPayload);
    if (list.length || isScreeningComplete(statusPayload)) return statusPayload;
    await sleep(1500);
  }

  return fetchScreeningResult(screeningId);
}

export async function runScreening({ role, jobDescription, screeningId, weights } = {}) {
  if (isMockApi()) {
    throw new Error('URL API belum diisi. Isi VITE_API_URL atau REACT_APP_API_URL terlebih dahulu. Hubungkan frontend ke FastAPI terlebih dahulu.');
  }

  const activeScreeningId = screeningId || latestScreeningId;

  let payload = null;
  if (activeScreeningId) {
    payload = await waitForScreening(activeScreeningId);
  } else {
    payload = await requestFirstAvailable(['/screen/', '/api/screening/run'], {
      method: 'POST',
      body: JSON.stringify({ role, job_description: jobDescription, weights }),
    });
    latestScreeningId = extractScreeningId(payload) || latestScreeningId;
  }

  if (latestScreeningId && !extractCandidateList(payload).length) {
    payload = await fetchScreeningResult(latestScreeningId);
  }

  const list = extractCandidateList(payload);
  return list.map(normalizeCandidate).sort((a, b) => b.score - a.score);
}

export function mergeCandidateHistory(previous = [], incoming = []) {
  const rows = [];
  const seen = new Set();

  [...(previous || []), ...(incoming || [])].forEach((candidate, index) => {
    if (!candidate) return;
    const batchId = candidate.batchId || candidate.batchLabel || 'batch-terbaru';
    const baseId = candidate.id || candidate.email || candidate.name || `candidate-${index}`;
    const stableId = String(baseId).startsWith(`${batchId}-`) ? String(baseId) : `${batchId}-${baseId}`;
    const key = `${batchId}::${stableId}`;
    if (seen.has(key)) return;
    seen.add(key);
    rows.push({ ...candidate, id: stableId, batchId });
  });

  return rows.sort((a, b) => Number(b.score || 0) - Number(a.score || 0));
}
