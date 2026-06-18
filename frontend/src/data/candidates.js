export const JOB_DESCRIPTIONS = {
  "Frontend Developer": `Kami mencari Frontend Developer yang berpengalaman membangun aplikasi web modern.

Kandidat wajib menguasai:
- React.js / JavaScript / TypeScript
- HTML, CSS, Tailwind atau CSS Modules
- Integrasi REST API
- Git dan kolaborasi tim

Tanggung jawab:
- Mengembangkan fitur front-end
- Membuat UI responsif dan user friendly
- Berkolaborasi dengan backend dan UI/UX
- Menjaga kualitas kode dan performa aplikasi`,

  "Backend Developer": `Kami mencari Backend Developer yang mampu membangun API yang aman, cepat, dan mudah dikembangkan.

Kandidat wajib menguasai:
- Node.js / Express atau framework backend sejenis
- Database SQL atau NoSQL
- REST API dan autentikasi JWT
- Git dan dokumentasi API

Tanggung jawab:
- Membuat endpoint API
- Mendesain struktur database
- Mengelola autentikasi dan otorisasi
- Optimasi performa server`,

  "Fullstack Developer": `Kami mencari Fullstack Developer yang mampu mengerjakan sisi frontend dan backend.

Kandidat wajib menguasai:
- React.js untuk frontend
- Node.js / Express untuk backend
- Database SQL atau NoSQL
- REST API, Git, dan deployment dasar

Tanggung jawab:
- Mengembangkan fitur end-to-end
- Integrasi frontend dengan backend
- Membuat struktur database
- Menjaga kualitas aplikasi secara menyeluruh`,

  "UI/UX Designer": `Kami mencari UI/UX Designer yang mampu membuat desain produk digital yang mudah digunakan.

Kandidat wajib menguasai:
- Figma atau tools desain sejenis
- User flow, wireframe, dan prototype
- Design system dasar
- Riset pengguna dasar

Tanggung jawab:
- Membuat wireframe dan high fidelity design
- Menyusun user flow
- Berkolaborasi dengan developer
- Melakukan evaluasi usability`,

  "Data Analyst": `Kami mencari Data Analyst yang mampu mengolah data menjadi insight bisnis.

Kandidat wajib menguasai:
- Excel / Google Sheets tingkat lanjut
- SQL dasar hingga menengah
- Dashboard BI seperti Tableau / Power BI
- Analisis dan visualisasi data

Tanggung jawab:
- Membersihkan dan mengolah data
- Membuat laporan dan dashboard
- Menemukan insight dari data
- Mendukung keputusan berbasis data`
};

export const JOB_ROLES = Object.keys(JOB_DESCRIPTIONS);

export const JOB_DESCRIPTION = JOB_DESCRIPTIONS["Frontend Developer"];

export const CANDIDATES = [
  {
    id: 1, name: "Budi Santoso", initials: "BS",
    colorAccent: "#6c63ff", colorBg: "rgba(108,99,255,0.15)",
    email: "budi.s@gmail.com", phone: "+62 812-3456-7890", location: "Jakarta",
    position: "Senior Frontend Developer", score: 93, status: "Sangat Cocok",
    education: { level: "S1", major: "Teknik Informatika", university: "Universitas Indonesia", gpa: "3.72", year: "2016-2020" },
    experience: { years: 5, label: "5 tahun" },
    skills: ["React","TypeScript","Next.js","Tailwind","Jest","Git","Redux","REST API"],
    scoreBreakdown: { skill: 96, experience: 92, education: 88, relevance: 95 },
    workHistory: [
      { company: "Tokopedia", role: "Senior Frontend Developer", period: "2021-sekarang", desc: "Migrasi 30+ halaman ke Next.js App Router, unit test Jest coverage >85%, mentoring junior." },
      { company: "Bukalapak", role: "Frontend Developer", period: "2020-2021", desc: "Komponen UI React + Tailwind, integrasi REST API, state management Redux." }
    ],
    cvText: "Budi Santoso\nbudi.s@gmail.com | +62 812-3456-7890 | Jakarta\n\nPENDIDIKAN\nS1 Teknik Informatika - Universitas Indonesia (2016-2020)\nIPK: 3.72\n\nPENGALAMAN\nSenior Frontend Developer - Tokopedia (2021-sekarang)\n- Migrasi 30+ halaman ke Next.js App Router\n- Unit test Jest coverage >85%\n- Mentoring 3 junior developer\n\nFrontend Developer - Bukalapak (2020-2021)\n- Komponen UI React + Tailwind\n- Integrasi REST API dengan Redux\n\nSKILL\nReact, TypeScript, Next.js, Tailwind, Jest, Git, Redux, REST API"
  },
  {
    id: 2, name: "Anisa Rahmawati", initials: "AR",
    colorAccent: "#34d399", colorBg: "rgba(52,211,153,0.12)",
    email: "anisa.r@gmail.com", phone: "+62 813-2345-6789", location: "Bandung",
    position: "Frontend Developer", score: 89, status: "Sangat Cocok",
    education: { level: "S1", major: "Sistem Informasi", university: "Institut Teknologi Bandung", gpa: "3.65", year: "2017-2021" },
    experience: { years: 4, label: "4 tahun" },
    skills: ["React","JavaScript","CSS Modules","Figma","Agile","REST API","Git"],
    scoreBreakdown: { skill: 88, experience: 86, education: 85, relevance: 90 },
    workHistory: [
      { company: "Gojek", role: "Frontend Developer", period: "2021-sekarang", desc: "Dashboard driver React, kolaborasi desain Figma, Agile/Scrum." },
      { company: "Grab", role: "Frontend Intern", period: "2020-2021", desc: "Komponen UI reusable, CSS Modules, styled-components." }
    ],
    cvText: "Anisa Rahmawati\nanisa.r@gmail.com | +62 813-2345-6789 | Bandung\n\nPENDIDIKAN\nS1 Sistem Informasi - ITB (2017-2021), IPK: 3.65\n\nPENGALAMAN\nFrontend Developer - Gojek (2021-sekarang)\nFrontend Intern - Grab (2020-2021)\n\nSKILL\nReact, JavaScript, CSS Modules, Figma, Agile, Git, REST API"
  },
  {
    id: 3, name: "Deni Kurniawan", initials: "DK",
    colorAccent: "#60a5fa", colorBg: "rgba(96,165,250,0.12)",
    email: "deni.k@gmail.com", phone: "+62 811-3456-7890", location: "Jakarta",
    position: "Lead Frontend Engineer", score: 86, status: "Sangat Cocok",
    education: { level: "S2", major: "Ilmu Komputer", university: "Universitas Gadjah Mada", gpa: "3.80", year: "2018-2020" },
    experience: { years: 6, label: "6 tahun" },
    skills: ["React","TypeScript","GraphQL","Cypress","Jest","Agile","Git","Apollo"],
    scoreBreakdown: { skill: 90, experience: 96, education: 92, relevance: 82 },
    workHistory: [
      { company: "Traveloka", role: "Lead Frontend Engineer", period: "2019-sekarang", desc: "Pimpin tim 5 developer, micro-frontend architecture, GraphQL + Apollo." },
      { company: "Tiket.com", role: "Frontend Engineer", period: "2017-2019", desc: "Fitur booking React, Cypress end-to-end testing." }
    ],
    cvText: "Deni Kurniawan\ndeni.k@gmail.com | +62 811-3456-7890 | Jakarta\n\nPENDIDIKAN\nS2 Ilmu Komputer - UGM (2018-2020)\nS1 Teknik Informatika - UGM (2014-2018)\n\nPENGALAMAN\nLead Frontend Engineer - Traveloka (2019-sekarang)\nFrontend Engineer - Tiket.com (2017-2019)\n\nSKILL\nReact, TypeScript, GraphQL, Cypress, Jest, Agile, Git, Apollo"
  },
  {
    id: 4, name: "Fitri Handayani", initials: "FH",
    colorAccent: "#f472b6", colorBg: "rgba(244,114,182,0.12)",
    email: "fitri.h@gmail.com", phone: "+62 857-1234-5678", location: "Surabaya",
    position: "Frontend Developer", score: 84, status: "Sangat Cocok",
    education: { level: "S1", major: "Teknik Informatika", university: "Institut Teknologi Sepuluh Nopember", gpa: "3.81", year: "2018-2022" },
    experience: { years: 3, label: "3 tahun" },
    skills: ["React","Next.js","Tailwind","TypeScript","Git","REST API"],
    scoreBreakdown: { skill: 85, experience: 80, education: 84, relevance: 86 },
    workHistory: [
      { company: "Shopee Indonesia", role: "Frontend Developer", period: "2022-sekarang", desc: "Halaman produk & cart Next.js, design system Tailwind + TypeScript." },
      { company: "Tokopedia", role: "Frontend Intern", period: "2021-2022", desc: "Fitur flash sale, komponen UI React." }
    ],
    cvText: "Fitri Handayani\nfitri.h@gmail.com | +62 857-1234-5678 | Surabaya\n\nPENDIDIKAN\nS1 Teknik Informatika - ITS (2018-2022), IPK: 3.81\n\nPENGALAMAN\nFrontend Developer - Shopee (2022-sekarang)\nFrontend Intern - Tokopedia (2021-2022)\n\nSKILL\nReact, Next.js, Tailwind, TypeScript, Git, REST API"
  },
  {
    id: 5, name: "Reza Mahendra", initials: "RM",
    colorAccent: "#a3e635", colorBg: "rgba(163,230,53,0.10)",
    email: "reza.m@gmail.com", phone: "+62 822-3456-7890", location: "Yogyakarta",
    position: "Frontend Engineer", score: 78, status: "Cocok",
    education: { level: "S1", major: "Teknik Elektro", university: "Universitas Diponegoro", gpa: "3.30", year: "2017-2021" },
    experience: { years: 4, label: "4 tahun" },
    skills: ["React","JavaScript","CSS","Bootstrap","REST API","Git"],
    scoreBreakdown: { skill: 76, experience: 82, education: 75, relevance: 78 },
    workHistory: [
      { company: "PT Astra Digital", role: "Frontend Engineer", period: "2021-sekarang", desc: "Antarmuka web React, Bootstrap, integrasi REST API." },
      { company: "Freelance", role: "Web Developer", period: "2019-2021", desc: "Website company profile React + jQuery." }
    ],
    cvText: "Reza Mahendra\nreza.m@gmail.com | Yogyakarta\n\nS1 Teknik Elektro - UNDIP (2017-2021)\n\nFrontend Engineer - Astra Digital (2021-sekarang)\nFreelance Web Developer (2019-2021)\n\nSKILL: React, JavaScript, CSS, Bootstrap, REST API, Git"
  },
  {
    id: 6, name: "Sari Dewi", initials: "SD",
    colorAccent: "#fb923c", colorBg: "rgba(251,146,60,0.12)",
    email: "sari.d@gmail.com", phone: "+62 878-2345-6789", location: "Malang",
    position: "Junior Frontend Developer", score: 74, status: "Cocok",
    education: { level: "D3", major: "Rekayasa Perangkat Lunak", university: "Politeknik Negeri Malang", gpa: "3.50", year: "2019-2022" },
    experience: { years: 2, label: "2 tahun" },
    skills: ["React","HTML","CSS","JavaScript","Git","Figma"],
    scoreBreakdown: { skill: 72, experience: 65, education: 68, relevance: 78 },
    workHistory: [
      { company: "CV Digital Solusi", role: "Frontend Developer", period: "2022-sekarang", desc: "UI React + CSS, maintenance website klien." }
    ],
    cvText: "Sari Dewi\nsari.d@gmail.com | Malang\n\nD3 RPL - Polinema (2019-2022)\n\nFrontend Developer - CV Digital Solusi (2022-sekarang)\n\nSKILL: React, HTML, CSS, JavaScript, Git, Figma"
  },
  {
    id: 7, name: "Andi Pratama", initials: "AP",
    colorAccent: "#94a3b8", colorBg: "rgba(148,163,184,0.10)",
    email: "andi.p@gmail.com", phone: "+62 819-3456-7890", location: "Semarang",
    position: "Fullstack Developer", score: 71, status: "Cocok",
    education: { level: "S1", major: "Matematika", university: "Universitas Negeri Semarang", gpa: "3.20", year: "2018-2022" },
    experience: { years: 3, label: "3 tahun" },
    skills: ["Vue.js","Python","Django","MySQL","Git","REST API"],
    scoreBreakdown: { skill: 65, experience: 74, education: 72, relevance: 70 },
    workHistory: [
      { company: "PT Solusi Digital", role: "Fullstack Developer", period: "2022-sekarang", desc: "Vue.js + Django, database MySQL." }
    ],
    cvText: "Andi Pratama\nandi.p@gmail.com | Semarang\n\nS1 Matematika - UNNES (2018-2022)\n\nFullstack Developer - PT Solusi Digital (2022-sekarang)\n\nSKILL: Vue.js, Python, Django, MySQL, Git"
  },
  {
    id: 8, name: "Lestari Wulan", initials: "LW",
    colorAccent: "#f87171", colorBg: "rgba(248,113,113,0.12)",
    email: "lestari.w@gmail.com", phone: "+62 856-4567-8901", location: "Bekasi",
    position: "Junior Frontend Developer", score: 68, status: "Cocok",
    education: { level: "S1", major: "Teknologi Informasi", university: "Universitas Gunadarma", gpa: "3.40", year: "2019-2023" },
    experience: { years: 2, label: "2 tahun" },
    skills: ["Angular","JavaScript","SASS","Bootstrap","TypeScript","Git"],
    scoreBreakdown: { skill: 65, experience: 62, education: 72, relevance: 70 },
    workHistory: [
      { company: "PT Kreasi Digital", role: "Junior Frontend Developer", period: "2023-sekarang", desc: "Angular + TypeScript, SASS, Bootstrap." }
    ],
    cvText: "Lestari Wulan\nlestari.w@gmail.com | Bekasi\n\nS1 Teknologi Informasi - Gunadarma (2019-2023)\n\nJunior Frontend Developer - PT Kreasi Digital (2023-sekarang)\n\nSKILL: Angular, JavaScript, TypeScript, SASS, Bootstrap, Git"
  },
  {
    id: 9, name: "Hendra Wijaya", initials: "HW",
    colorAccent: "#818cf8", colorBg: "rgba(129,140,248,0.12)",
    email: "hendra.w@gmail.com", phone: "+62 895-3456-7890", location: "Depok",
    position: "Junior Developer", score: 62, status: "Perlu Review",
    education: { level: "S1", major: "Teknik Informatika", university: "Universitas Pancasila", gpa: "3.21", year: "2019-2023" },
    experience: { years: 1, label: "1 tahun" },
    skills: ["React","HTML","CSS","JavaScript","Git"],
    scoreBreakdown: { skill: 60, experience: 52, education: 72, relevance: 63 },
    workHistory: [
      { company: "Startup XYZ", role: "Junior Frontend Developer", period: "2023-sekarang", desc: "Halaman web React, Tailwind CSS dasar." }
    ],
    cvText: "Hendra Wijaya\nhendra.w@gmail.com | Depok\n\nS1 Teknik Informatika - Universitas Pancasila (2019-2023), IPK: 3.21\n\nJunior Frontend Developer - Startup XYZ (2023-sekarang)\n\nSKILL: React, HTML, CSS, JavaScript, Git"
  },
  {
    id: 10, name: "Mega Utami", initials: "MU",
    colorAccent: "#34d399", colorBg: "rgba(52,211,153,0.10)",
    email: "mega.u@gmail.com", phone: "+62 812-9876-5432", location: "Tangerang",
    position: "Fresh Graduate", score: 55, status: "Perlu Review",
    education: { level: "S1", major: "Sistem Informasi", university: "Universitas Mercu Buana", gpa: "3.45", year: "2020-2024" },
    experience: { years: 0, label: "Fresh grad" },
    skills: ["HTML","CSS","JavaScript","Bootstrap","Git"],
    scoreBreakdown: { skill: 52, experience: 40, education: 68, relevance: 58 },
    workHistory: [],
    cvText: "Mega Utami\nmega.u@gmail.com | Tangerang\n\nS1 Sistem Informasi - Mercu Buana (2020-2024), IPK: 3.45\n\nBelum ada pengalaman kerja profesional.\nProyek: Website portofolio HTML/CSS/JS, landing page Bootstrap.\n\nSKILL: HTML, CSS, JavaScript, Bootstrap, Git"
  }
];
