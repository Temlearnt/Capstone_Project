// ============================================================
// NLP SERVICE — Placeholder untuk integrasi AI/Anthropic
// ============================================================
// File ini berisi skeleton fungsi yang akan diisi dengan
// pemanggilan Anthropic API (claude-sonnet-4-20250514)
//
// Flow yang akan diimplementasikan:
//   1. extractCVInfo(pdfText)     → parsing CV dengan AI
//   2. scoreCandidate(cv, jd)     → scoring relevansi vs JD
//   3. rankCandidates(list, jd)   → batch ranking semua CV
// ============================================================

/**
 * Ekstrak informasi dari teks CV menggunakan AI
 * @param {string} pdfText - Teks mentah dari PDF
 * @param {string} jobDescription - JD untuk konteks ekstraksi
 * @returns {Promise<Object>} - Data kandidat terstruktur
 *
 * TODO: Implementasi dengan Anthropic API
 * Contoh prompt:
 *   "Ekstrak informasi berikut dari CV ini: nama, email, telepon,
 *    pendidikan (jenjang, jurusan, universitas, IPK), pengalaman kerja
 *    (daftar posisi, perusahaan, periode, deskripsi), dan skill teknis.
 *    Kembalikan dalam format JSON."
 */
export async function extractCVInfo(pdfText, jobDescription) {
  // === DUMMY IMPLEMENTATION ===
  // Hapus bagian ini saat integrasi API nyata
  console.log('[NLP] extractCVInfo dipanggil (dummy mode)')
  await new Promise(r => setTimeout(r, 1200)) // simulasi delay API

  // Kembalikan objek kosong — akan diisi oleh AI
  return {
    name: '',
    email: '',
    phone: '',
    location: '',
    education: { level: '', major: '', university: '', gpa: '', year: '' },
    experience: { years: 0, label: '', jobs: [] },
    skills: [],
  }
}

/**
 * Hitung skor kesesuaian kandidat terhadap Job Description
 * @param {Object} candidateInfo - Hasil dari extractCVInfo
 * @param {string} jobDescription - Teks JD
 * @returns {Promise<Object>} - Skor dan breakdown
 *
 * TODO: Implementasi dengan Anthropic API
 * Contoh prompt:
 *   "Berdasarkan JD berikut dan profil kandidat ini, berikan skor
 *    kesesuaian 0-100 untuk kategori: skill (bobot 40%), pengalaman (30%),
 *    pendidikan (15%), dan relevansi keseluruhan (15%).
 *    Kembalikan JSON: { skill, experience, education, relevance, total, status }"
 */
export async function scoreCandidate(candidateInfo, jobDescription) {
  // === DUMMY IMPLEMENTATION ===
  console.log('[NLP] scoreCandidate dipanggil (dummy mode)')
  await new Promise(r => setTimeout(r, 800))

  return {
    skill: 0,
    experience: 0,
    education: 0,
    relevance: 0,
    total: 0,
    status: 'Perlu Review',
  }
}

/**
 * Proses batch: ekstrak + score semua CV terhadap 1 JD
 * @param {Array<{fileName, text}>} cvList - Daftar CV
 * @param {string} jobDescription - JD aktif
 * @param {Function} onProgress - Callback (index, total)
 * @returns {Promise<Array>} - Daftar kandidat terurut
 *
 * TODO: Implementasi loop extractCVInfo + scoreCandidate
 */
export async function rankCandidates(cvList, jobDescription, onProgress) {
  console.log('[NLP] rankCandidates dipanggil (dummy mode)')
  const results = []

  for (let i = 0; i < cvList.length; i++) {
    if (onProgress) onProgress(i + 1, cvList.length)
    const info = await extractCVInfo(cvList[i].text, jobDescription)
    const score = await scoreCandidate(info, jobDescription)
    results.push({ ...info, ...score, fileName: cvList[i].fileName })
  }

  return results.sort((a, b) => b.total - a.total)
}

// ============================================================
// HELPER: Baca PDF di browser (PDF.js atau pdfmake)
// TODO: Integrasikan dengan pdf.js untuk ekstraksi teks PDF
// ============================================================
export async function extractTextFromPDF(file) {
  console.log('[NLP] extractTextFromPDF dipanggil (dummy mode) :', file.name)
  // TODO: gunakan pdfjsLib untuk ekstraksi teks asli
  return `[Teks dari ${file.name} akan diekstrak di sini menggunakan PDF.js]`
}
