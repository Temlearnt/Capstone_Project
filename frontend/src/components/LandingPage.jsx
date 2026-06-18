import React, { useState } from 'react';
import {
  ArrowRight,
  BrainCircuit,
  BarChart3,
  CheckCircle2,
  FileSearch,
  LayoutDashboard,
  Mail,
  MapPin,
  Phone,
  ShieldCheck,
  Sparkles,
  UploadCloud,
} from 'lucide-react';
import recruitlyLogo from '../assets/recruitly-logo.png';
import teamPhoto1 from '../assets/team-1.jpeg';
import teamPhoto2 from '../assets/team-2.jpeg';
import teamPhoto3 from '../assets/team-3.jpeg';
import teamPhoto4 from '../assets/team-4.jpeg';
import './LandingPage.css';

const TEAM_MEMBERS = [
  { name: 'I Putu Sutha S', role: 'Backend Engginer', photo: teamPhoto2 },
  { name: 'Ilyas Lucky F', role: 'NLP Engginer', photo: teamPhoto3 },
  { name: 'M Fathir Afif', role: 'Frontend Engginer', photo: teamPhoto4 },
  { name: 'Ryan Nanda Saputra H', role: 'Data Engginer', photo: teamPhoto1 },
];

export default function LandingPage({ user, onLogin, onRegister, onDashboard }) {
  const [contactForm, setContactForm] = useState({
    name: '',
    email: '',
    subject: 'Masukan untuk Recruitly',
    message: '',
  });

  const goTo = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const handleContactChange = (event) => {
    const { name, value } = event.target;
    setContactForm((current) => ({ ...current, [name]: value }));
  };

  const handleContactSubmit = (event) => {
    event.preventDefault();

    const emailTo = 'fathirafifm@gmail.com';
    const subject = encodeURIComponent(contactForm.subject || 'Masukan untuk Recruitly');
    const body = encodeURIComponent(
      `Nama: ${contactForm.name}\n` +
      `Email: ${contactForm.email}\n\n` +
      `Pesan / Kritik / Saran / Masalah:\n${contactForm.message}`
    );

    window.location.href = `mailto:${emailTo}?subject=${subject}&body=${body}`;
  };

  return (
    <div className="landing-page">
      <header className="landing-topbar">
        <nav className="landing-nav">
          <button className="landing-brand" onClick={() => goTo('beranda')} aria-label="Kembali ke beranda">
            <img src={recruitlyLogo} alt="Recruitly" className="landing-logo-img" />
          </button>

          <div className="landing-menu">
            <button onClick={() => goTo('beranda')}>Beranda</button>
            <button onClick={() => goTo('about')}>About</button>
            <button onClick={() => goTo('features')}>Features</button>
            <button onClick={() => goTo('team')}>Team</button>
            <button onClick={() => goTo('contact')}>Contact Us</button>
          </div>

          <div className="landing-nav-actions">
            {user ? (
              <button className="landing-btn landing-btn-primary" onClick={onDashboard}>Buka Dashboard</button>
            ) : (
              <>
                <button className="landing-btn landing-btn-outline" onClick={onLogin}>Login</button>
                <button className="landing-btn landing-btn-primary" onClick={onRegister}>Register</button>
              </>
            )}
          </div>
        </nav>
      </header>

      <main>
        <section id="beranda" className="landing-section landing-hero">
          <div className="landing-copy">
            <div className="landing-badge">
              <Sparkles size={16} /> AI Recruitment Screening Platform
            </div>
            <h1>
              Screening CV kandidat jadi lebih <span>cepat, rapi, dan objektif.</span>
            </h1>
            <p>
              Recruitly membantu recruiter mengunggah CV, mencocokkan kandidat dengan job description,
              lalu menampilkan kandidat terbaik dengan teknologi AI yang akurat dan modern.
            </p>
            <div className="landing-actions">
              <button className="landing-btn landing-btn-primary landing-cta" onClick={user ? onDashboard : onLogin}>
                {user ? 'Masuk Dashboard' : 'Mulai Sekarang'} <ArrowRight size={18} />
              </button>
              {!user && (
                <button className="landing-btn landing-btn-outline landing-cta" onClick={onRegister}>
                  Buat Akun Company
                </button>
              )}
            </div>
          </div>

          <div className="landing-preview" aria-label="Preview candidate match Recruitly">
            <div className="preview-card preview-main">
              <div className="preview-header">
                <span>Candidate Match</span>
                <div>
                  <b>93%</b>
                  <small>Overall Match</small>
                </div>
              </div>
              <div className="preview-person">
                <div className="preview-avatar">BS</div>
                <div>
                  <strong>Budi Santoso</strong>
                  <span>Senior Frontend Developer</span>
                </div>
              </div>
              <div className="preview-bars">
                <PreviewBar label="Skill Match" value="96%" />
                <PreviewBar label="Pengalaman" value="92%" />
                <PreviewBar label="Relevansi JD" value="95%" />
              </div>
            </div>
            <div className="preview-file-card">
              <FileSearch size={34} />
              <span>CV</span>
              <CheckCircle2 size={28} />
            </div>
            <div className="preview-glow" />
          </div>
        </section>


        <section id="about" className="landing-section landing-about">
          <div className="section-heading">
            <span>About</span>
            <h2>Tentang Recruitly</h2>
            <p>
              Platform AI Recruitment Screening yang membantu perusahaan menemukan kandidat terbaik
              secara lebih cepat, objektif, dan transparan.
            </p>
          </div>

          <div className="about-card">
            <p>
              Recruitly adalah platform AI Recruitment Screening yang membantu recruiter melakukan screening CV,
              mencocokkan kandidat dengan Job Description, dan menghasilkan ranking kandidat secara otomatis.
            </p>
            <p>
              Tujuan Recruitly adalah membantu proses rekrutmen menjadi lebih cepat, akurat, dan objektif,
              sehingga perusahaan dapat menemukan kandidat terbaik dengan proses yang lebih efisien.
            </p>
          </div>
        </section>

        <section id="features" className="landing-section landing-features">
          <div className="section-heading">
            <span>Features</span>
            <h2>Fitur Utama Recruitly</h2>
            <p>Empat fitur utama yang membantu proses recruitment dari upload CV sampai analisis kandidat.</p>
          </div>

          <div className="features-grid">
            <Feature icon={<BrainCircuit size={24} />} title="AI Screening" text="Analisis CV secara otomatis menggunakan AI untuk membaca kecocokan kandidat." />
            <Feature icon={<FileSearch size={24} />} title="Resume Parsing" text="Ekstraksi informasi penting dari CV PDF seperti skill, pengalaman, dan pendidikan." />
            <Feature icon={<BarChart3 size={24} />} title="Candidate Ranking" text="Peringkat kandidat berdasarkan skor kecocokan terhadap Job Description." />
            <Feature icon={<LayoutDashboard size={24} />} title="Dashboard Analytics" text="Visualisasi hasil screening dan detail kandidat dalam dashboard yang rapi." />
          </div>
        </section>

        <section id="team" className="landing-section landing-team">
          <div className="section-heading">
            <span>Team</span>
            <h2>Team Kami</h2>
            <p>Empat orang di balik pengembangan Recruitly.</p>
          </div>

          <div className="team-grid">
            {TEAM_MEMBERS.map(member => (
              <article className="team-card" key={member.name}>
                <div className="team-photo"><img src={member.photo} alt={member.name} /></div>
                <h3>{member.name}</h3>
                <p>{member.role}</p>
              </article>
            ))}
          </div>
        </section>

        <section id="contact" className="landing-section landing-contact">
          <div className="section-heading">
            <span>Contact Us</span>
            <h2>Kirim Masukan untuk Recruitly</h2>
            <p>Pengunjung bisa mengirim masukan, kritik, saran, atau melaporkan masalah yang terjadi melalui form berikut.</p>
          </div>

          <div className="contact-layout">
            <div className="contact-info-card">
              <h3>Kami siap mendengarkan</h3>
              <p>Setiap pesan akan membantu Recruitly menjadi platform screening CV yang lebih baik, cepat, dan nyaman digunakan.</p>
              <ContactItem icon={<Mail size={20} />} title="Email Tujuan" text="fathirafifm@gmail.com" />
              <ContactItem icon={<Phone size={20} />} title="Telepon" text="+62 823-1648-2370" />
              <ContactItem icon={<MapPin size={20} />} title="Lokasi" text="Jakarta, Indonesia" />
            </div>

            <form className="contact-form-card" onSubmit={handleContactSubmit}>
              <div className="form-row">
                <label>
                  Nama
                  <input
                    type="text"
                    name="name"
                    placeholder="Masukkan nama Anda"
                    value={contactForm.name}
                    onChange={handleContactChange}
                    required
                  />
                </label>
                <label>
                  Email
                  <input
                    type="email"
                    name="email"
                    placeholder="nama@email.com"
                    value={contactForm.email}
                    onChange={handleContactChange}
                    required
                  />
                </label>
              </div>

              <label>
                Judul Pesan
                <input
                  type="text"
                  name="subject"
                  placeholder="Contoh: Saran fitur dashboard"
                  value={contactForm.subject}
                  onChange={handleContactChange}
                  required
                />
              </label>

              <label>
                Masukan / Kritik / Saran / Masalah
                <textarea
                  name="message"
                  placeholder="Tulis pesan Anda di sini..."
                  value={contactForm.message}
                  onChange={handleContactChange}
                  rows={7}
                  required
                />
              </label>

              <button className="landing-btn landing-btn-primary contact-submit" type="submit">
                Kirim ke Email <ArrowRight size={18} />
              </button>
              <small>Form ini akan membuka aplikasi email di perangkat pengunjung dengan isi pesan otomatis.</small>
            </form>
          </div>
        </section>

        <footer className="landing-footer">
          <div>
            <img src={recruitlyLogo} alt="Recruitly" className="footer-logo-img" />
            <p>AI Recruitment Screening Platform</p>
          </div>
          <span>© 2026 Recruitly. All rights reserved.</span>
        </footer>
      </main>
    </div>
  );
}

function PreviewBar({ label, value }) {
  return (
    <div className="preview-bar-row">
      <span>{label}</span>
      <div><i style={{ width: value }} /></div>
      <b>{value}</b>
    </div>
  );
}

function Feature({ icon, title, text }) {
  return (
    <article className="landing-feature">
      <div>{icon}</div>
      <h3>{title}</h3>
      <p>{text}</p>
    </article>
  );
}

function ContactItem({ icon, title, text }) {
  return (
    <article className="contact-item">
      <div>{icon}</div>
      <span>{title}</span>
      <strong>{text}</strong>
    </article>
  );
}
