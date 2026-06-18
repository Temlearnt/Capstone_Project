import React, { useState, useRef } from 'react';
import { JOB_ROLES } from '../../data/candidates';
import { uploadCVFiles, runScreening } from '../../services/candidateService';
import recruitlyLoadingLogo from '../../assets/recruitly-loading-logo.png';
import './UploadPage.css';

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB

export default function UploadPage({ jobDescription, selectedRole, jobDescriptions = {}, onRoleChange, onJDChange, onGoRanking, onCandidatesUpdate }) {
  const [files, setFiles] = useState([]);
  const [dragging, setDragging] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [processMessage, setProcessMessage] = useState('');
  const [processError, setProcessError] = useState('');
  const [screeningProgress, setScreeningProgress] = useState(0);
  const inputRef = useRef();
  const [weights, setWeights] = useState({
    skill: 40,
    education: 30,
    experience: 30,
  });
  const roleOptions = Object.keys(jobDescriptions || {}).length ? Object.keys(jobDescriptions) : JOB_ROLES;

  const updateWeight = (key, value) => {
    const numericValue = Math.max(0, Math.min(100, Number(value) || 0));
    setWeights(prev => ({ ...prev, [key]: numericValue }));
  };

  const isDuplicate = (file, currentFiles) => (
    currentFiles.some(item => (
      item.name === file.name && item.size === file.size && item.lastModified === file.lastModified
    ))
  );

  const addFiles = (selectedFiles) => {
    const pdfFiles = Array.from(selectedFiles || []);
    const validFiles = [];
    const rejected = [];

    pdfFiles.forEach(file => {
      const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');

      if (!isPdf) {
        rejected.push(`${file.name}: bukan file PDF`);
        return;
      }

      if (file.size > MAX_FILE_SIZE) {
        rejected.push(`${file.name}: ukuran lebih dari 5 MB`);
        return;
      }

      validFiles.push(file);
    });

    if (rejected.length > 0) {
      alert(`Beberapa file tidak bisa diunggah:\n${rejected.join('\n')}`);
    }

    if (validFiles.length === 0) return;

    setFiles(prev => {
      const nextFiles = [...prev];

      validFiles.forEach(file => {
        if (!isDuplicate(file, nextFiles)) {
          nextFiles.push({
            id: `${file.name}-${file.size}-${file.lastModified}`,
            name: file.name,
            size: file.size,
            lastModified: file.lastModified,
            file,
            status: 'ready',
          });
        }
      });

      return nextFiles;
    });
  };

  const handleFileInput = (e) => {
    addFiles(e.target.files);
    e.target.value = '';
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    addFiles(e.dataTransfer.files);
  };

  const removeFile = (id) => setFiles(prev => prev.filter(file => file.id !== id));

  const wait = (ms) => new Promise(resolve => window.setTimeout(resolve, ms));

  const updateScreeningStep = async (message, progress, duration = 700) => {
    setProcessMessage(message);
    setScreeningProgress(progress);
    await wait(duration);
  };

  async function handleRunScreening() {
    if (files.length === 0 || processing) return;

    setProcessing(true);
    setProcessError('');
    setScreeningProgress(4);

    try {
      await updateScreeningStep('Menyiapkan pipeline AI screening...', 12, 650);
      await updateScreeningStep('Mengunggah CV kandidat ke backend...', 26, 500);
      await uploadCVFiles({ files, role: selectedRole, jobDescription, weights });

      await updateScreeningStep('Membaca struktur CV dan metadata file...', 42, 800);
      await updateScreeningStep('Mengekstrak skill, pengalaman, pendidikan, dan bobot penilaian...', 58, 900);
      await updateScreeningStep(`Mencocokkan CV dengan role ${selectedRole}...`, 74, 800);
      await updateScreeningStep('Menjalankan NLP matching dan menghitung skor berbobot...', 86, 650);

      const rankedCandidates = await runScreening({ role: selectedRole, jobDescription, weights });

      await updateScreeningStep('Menyusun ranking kandidat terbaik...', 96, 700);

      if (rankedCandidates?.length && onCandidatesUpdate) {
        onCandidatesUpdate(prevCandidates => {
          const previous = Array.isArray(prevCandidates) ? prevCandidates : [];
          const currentBatchCount = new Set(previous.map(item => item.batchId || item.batchLabel).filter(Boolean)).size;
          const fallbackBatchId = `batch-${Date.now()}`;
          const firstBatchId = rankedCandidates[0]?.batchId;
          const batchId = firstBatchId && firstBatchId !== 'batch-terbaru' ? firstBatchId : fallbackBatchId;
          const firstBatchLabel = rankedCandidates[0]?.batchLabel;
          const batchLabel = firstBatchLabel && firstBatchLabel !== 'Batch terbaru'
            ? firstBatchLabel
            : `Batch ${currentBatchCount + 1} - Upload ${files.length} CV`;
          const uploadedAt = new Date().toLocaleString('id-ID');
          const currentBatch = rankedCandidates.map((candidate, index) => ({
            ...candidate,
            id: `${batchId}-${candidate.id || candidate.email || candidate.name || index}`,
            batchId,
            batchLabel,
            uploadedAt: candidate.uploadedAt || uploadedAt,
          }));
          return [...previous, ...currentBatch].sort((a, b) => Number(b.score || 0) - Number(a.score || 0));
        });
      }

      setFiles(prev => prev.map(file => ({ ...file, status: 'done' })));
      await updateScreeningStep('Screening selesai. Membuka halaman ranking...', 100, 550);
      onGoRanking();
    } catch (err) {
      setProcessError(err.message || 'Gagal memproses CV. Pastikan backend sudah berjalan.');
      setProcessMessage('');
      setScreeningProgress(0);
    } finally {
      setProcessing(false);
    }
  }

  return (
    <div className="upload-page">
      <div className="up-card">
        <div className="up-card-hdr jd-upload-hdr">
          <span className="card-title">Job Description</span>
          <div className="upload-role-inline">
            <span>Role</span>
            <select className="upload-role-select" value={selectedRole} onChange={e => onRoleChange(e.target.value)}>
              {roleOptions.map(role => <option key={role} value={role}>{role}</option>)}
            </select>
          </div>
        </div>
        <div className="up-card-body">
          <textarea
            className="jd-input"
            value={jobDescription}
            onChange={e => onJDChange(e.target.value)}
            placeholder="Tempelkan job description di sini..."
            rows={7}
          />
        </div>
      </div>

      <div className="up-card">
        <div className="up-card-hdr">
          <span className="card-title">Penilaian Bobot</span>
        </div>
        <div className="up-card-body">
          <div className="weight-helper">
            Atur bobot kemiripan CV terhadap job description. Setiap bobot bisa diatur bebas dari 0-100% tanpa harus berjumlah 100%.
          </div>

          <div className="weight-grid">
            <label className="weight-item">
              <div className="weight-top">
                <span>Skill</span>
                <strong>{weights.skill}%</strong>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={weights.skill}
                onChange={e => updateWeight('skill', e.target.value)}
              />
              <input
                type="number"
                min="0"
                max="100"
                value={weights.skill}
                onChange={e => updateWeight('skill', e.target.value)}
              />
            </label>

            <label className="weight-item">
              <div className="weight-top">
                <span>Pendidikan</span>
                <strong>{weights.education}%</strong>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={weights.education}
                onChange={e => updateWeight('education', e.target.value)}
              />
              <input
                type="number"
                min="0"
                max="100"
                value={weights.education}
                onChange={e => updateWeight('education', e.target.value)}
              />
            </label>

            <label className="weight-item">
              <div className="weight-top">
                <span>Pengalaman</span>
                <strong>{weights.experience}%</strong>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={weights.experience}
                onChange={e => updateWeight('experience', e.target.value)}
              />
              <input
                type="number"
                min="0"
                max="100"
                value={weights.experience}
                onChange={e => updateWeight('experience', e.target.value)}
              />
            </label>
          </div>
        </div>
      </div>

      <div className="up-card">
        <div className="up-card-hdr">
          <span className="card-title">Unggah CV Kandidat</span>
          <span className="upload-hint">Bisa pilih beberapa file · Format PDF</span>
        </div>
        <div className="up-card-body">
          <input
            ref={inputRef}
            type="file"
            accept="application/pdf,.pdf"
            multiple
            style={{ display: 'none' }}
            onChange={handleFileInput}
          />

          <div
            className={`drop-zone${dragging ? ' dragging' : ''}`}
            onClick={() => inputRef.current?.click()}
            onDragOver={e => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
          >
            <div className="drop-icon">📄</div>
            <div className="drop-title">Klik untuk pilih CV dari komputer</div>
            <div className="drop-sub">atau drag & drop file PDF · maks. 5 MB</div>
            <div className="drop-note">
              File yang dipilih akan masuk ke daftar unggahan terlebih dahulu.<br />
              CV tidak langsung muncul otomatis sebelum kamu memilih file.
            </div>
          </div>

          {files.length > 0 && (
            <div className="file-list">
              {files.map(file => (
                <div key={file.id} className="file-item">
                  <span className="file-icon">📄</span>
                  <span className="file-name">{file.name}</span>
                  <span className="file-status">{file.status === 'done' ? 'Selesai' : 'Siap diproses'}</span>
                  <button className="file-remove" onClick={() => removeFile(file.id)}>×</button>
                </div>
              ))}
            </div>
          )}

          {files.length > 0 && (
            <div className="up-actions">
              <button className="btn-run" onClick={handleRunScreening} disabled={processing}>
                {processing ? '⏳ Memproses CV...' : '⚡ Jalankan Screening AI'}
              </button>
              <span className="up-actions-note">
                {processMessage || `${files.length} CV siap diproses`}
              </span>
            </div>
          )}

          {processError && <div className="upload-error">{processError}</div>}
        </div>
      </div>

      {processing && (
        <div className="screening-overlay" role="status" aria-live="polite">
          <div className="screening-modal">
            <div className="screening-orbit">
              <span className="orbit-dot dot-one" />
              <span className="orbit-dot dot-two" />
              <span className="orbit-dot dot-three" />
              <div className="screening-core">AI</div>
            </div>

            <img src={recruitlyLoadingLogo} alt="Recruitly" className="upload-screening-logo" />
            <div className="screening-kicker">Recruitly NLP Engine</div>
            <h2>Screening CV Kandidat</h2>
            <p>{processMessage || 'Memproses CV kandidat...'}</p>

            <div className="screening-progress">
              <div className="screening-progress-fill" style={{ width: `${screeningProgress}%` }} />
            </div>
            <div className="screening-percent">{screeningProgress}%</div>

            <div className="screening-steps">
              <span className={screeningProgress >= 26 ? 'active' : ''}>Upload</span>
              <span className={screeningProgress >= 58 ? 'active' : ''}>Extract</span>
              <span className={screeningProgress >= 86 ? 'active' : ''}>Analyze</span>
              <span className={screeningProgress >= 100 ? 'active' : ''}>Rank</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
