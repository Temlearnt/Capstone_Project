// ─── NLP / AI Service (Placeholder) ───────────────────────────────────────
//
// Folder ini disiapkan untuk integrasi AI scoring dan ekstraksi CV.
// Saat ini semua fungsi mengembalikan data dummy.
//
// TODO (integrasi berikutnya):
//   1. extractCVText(file)      → gunakan pdf-parse / pdfjs untuk ekstrak teks dari PDF
//   2. extractCandidateInfo()   → kirim teks ke Anthropic API untuk ekstrak nama, email, skill, dll
//   3. scoreCandidate()         → bandingkan profil kandidat dengan JD menggunakan AI
//   4. rankCandidates()         → urutkan hasil berdasarkan skor
//
// Contoh integrasi Anthropic API:
//
// export async function scoreCandidate(cvText, jobDescription) {
//   const response = await fetch("https://api.anthropic.com/v1/messages", {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({
//       model: "claude-sonnet-4-20250514",
//       max_tokens: 1000,
//       messages: [{
//         role: "user",
//         content: `Nilai kesesuaian CV ini dengan job description.
//           CV: ${cvText}
//           JD: ${jobDescription}
//           Kembalikan JSON: { score, breakdown: { skill, experience, education, relevance }, skills[], summary }`
//       }]
//     })
//   });
//   const data = await response.json();
//   return JSON.parse(data.content[0].text);
// }

/**
 * Simulasi ekstraksi teks dari PDF (dummy)
 * @param {File} file - File PDF yang diupload
 * @returns {Promise<string>} Teks hasil ekstraksi
 */
export async function extractCVText(file) {
  // TODO: implementasi dengan pdf-parse atau pdfjs-dist
  await new Promise(r => setTimeout(r, 800)); // simulasi delay
  return `[Teks dari ${file.name} akan diekstrak di sini setelah integrasi NLP]`;
}

/**
 * Simulasi ekstraksi informasi kandidat dari teks CV (dummy)
 * @param {string} cvText - Teks CV
 * @returns {Promise<Object>} Informasi kandidat
 */
export async function extractCandidateInfo(cvText) {
  // TODO: kirim ke Anthropic API untuk ekstraksi terstruktur
  await new Promise(r => setTimeout(r, 600));
  return {
    name: "Kandidat Baru",
    email: "kandidat@email.com",
    phone: "-",
    location: "-",
    skills: [],
    education: { level: "-", major: "-", university: "-", gpa: "-" },
    experience: { years: 0, label: "Tidak diketahui" },
    workHistory: [],
  };
}

/**
 * Simulasi scoring kandidat vs job description (dummy)
 * @param {Object} candidateInfo - Informasi kandidat
 * @param {string} jobDescription - Teks job description
 * @returns {Promise<Object>} Skor dan breakdown
 */
export async function scoreCandidate(candidateInfo, jobDescription) {
  // TODO: kirim ke Anthropic API untuk scoring
  await new Promise(r => setTimeout(r, 1000));
  return {
    score: Math.floor(Math.random() * 40 + 50),
    status: "Cocok",
    scoreBreakdown: { skill: 70, experience: 65, education: 70, relevance: 68 },
  };
}
