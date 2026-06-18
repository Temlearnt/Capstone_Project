import { useState, useRef } from 'react'
import { useApp } from '../../hooks/useAppContext'
import { Card, CardHeader, Btn } from '../ui'
import { Upload, FileText, CheckCircle, X, Cpu, AlertTriangle } from 'lucide-react'
import { extractTextFromPDF, rankCandidates } from '../../services/nlpService'

// ============================================================
// Catatan: Proses NLP saat ini menggunakan dummy data.
// Integrasi Anthropic API ada di: src/services/nlpService.js
// ============================================================

const DUMMY_FILES = [
  'Budi_Santoso_CV.pdf',
  'Anisa_Rahmawati_CV.pdf',
  'Deni_Kurniawan_CV.pdf',
  'Fitri_Handayani_CV.pdf',
]

export default function UploadPage({ setPage }) {
  const { jobDescription, setJobDescription } = useApp()
  const [files, setFiles] = useState([])
  const [running, setRunning] = useState(false)
  const [progress, setProgress] = useState(null)
  const [dummyIdx, setDummyIdx] = useState(0)
  const inputRef = useRef()

  function handleFileInput(e) {
    const f = e.target.files[0]
    if (!f) return
    if (f.type !== 'application/pdf') {
      alert('Hanya file PDF yang diperbolehkan.')
      return
    }
    addFile(f.name, f)
  }

  function addFile(name, fileObj) {
    setFiles(prev => [...prev, {
      id: Date.now(),
      name,
      file: fileObj,
      status: 'ready',
    }])
  }

  function simulateDummyUpload() {
    if (dummyIdx >= DUMMY_FILES.length) return
    addFile(DUMMY_FILES[dummyIdx])
    setDummyIdx(i => i + 1)
  }

  function removeFile(id) {
    setFiles(prev => prev.filter(f => f.id !== id))
  }

  async function handleRun() {
    if (!files.length || !jobDescription.trim()) return
    setRunning(true)
    setProgress({ current: 0, total: files.length, label: 'Memulai proses...' })

    // TODO: Ganti dummy loop ini dengan nlpService.rankCandidates()
    for (let i = 0; i < files.length; i++) {
      setProgress({ current: i + 1, total: files.length, label: `Memproses: ${files[i].name}` })
      await new Promise(r => setTimeout(r, 800))
      setFiles(prev => prev.map(f => f.id === files[i].id ? { ...f, status: 'done' } : f))
    }

    setRunning(false)
    setProgress(null)
    setTimeout(() => setPage('ranking'), 400)
  }

  const canRun = files.length > 0 && jobDescription.trim().length > 20

  return (
    <div className="page-enter" style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 16 }}>

      {/* Notice dummy */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 10,
        padding: '10px 14px', borderRadius: 10,
        background: 'var(--amber-soft)', border: '1px solid var(--amber)',
        fontSize: 12, color: 'var(--amber)',
      }}>
        <AlertTriangle size={15} />
        Mode demo aktif — NLP/AI belum diintegrasikan. Lihat <code style={{ fontFamily: 'var(--mono)', fontSize: 11 }}>src/services/nlpService.js</code> untuk implementasi.
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
        {/* Upload zone */}
        <Card>
          <CardHeader title="Unggah CV kandidat" right={
            <span style={{ fontSize: 11, color: 'var(--text-3)' }}>Satu per satu • PDF</span>
          } />
          <div style={{ padding: 14 }}>
            {/* Real upload input (hidden) */}
            <input
              ref={inputRef}
              type="file"
              accept="application/pdf"
              style={{ display: 'none' }}
              onChange={handleFileInput}
            />

            {/* Drop zone */}
            <div
              onClick={() => inputRef.current?.click()}
              onDragOver={e => e.preventDefault()}
              onDrop={e => {
                e.preventDefault()
                const f = e.dataTransfer.files[0]
                if (f?.type === 'application/pdf') addFile(f.name, f)
              }}
              style={{
                border: '1.5px dashed var(--border-2)',
                borderRadius: 12, padding: 28, textAlign: 'center',
                cursor: 'pointer', background: 'var(--bg-3)',
                transition: 'var(--transition)',
              }}
              onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--accent)'}
              onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border-2)'}
            >
              <Upload size={28} color="var(--text-3)" style={{ marginBottom: 8 }} />
              <div style={{ fontSize: 13, color: 'var(--text-2)' }}>Klik atau drag & drop PDF</div>
              <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 4 }}>Maksimal 5MB per file</div>
            </div>

            {/* Dummy upload button (untuk demo) */}
            <div style={{ textAlign: 'center', marginTop: 10 }}>
              <button
                onClick={simulateDummyUpload}
                disabled={dummyIdx >= DUMMY_FILES.length}
                style={{
                  fontSize: 11, color: 'var(--text-3)', background: 'none',
                  border: 'none', cursor: dummyIdx < DUMMY_FILES.length ? 'pointer' : 'not-allowed',
                  textDecoration: 'underline', opacity: dummyIdx >= DUMMY_FILES.length ? .4 : 1,
                }}
              >
                + Tambah file dummy (demo)
              </button>
            </div>

            {/* File list */}
            {files.length > 0 && (
              <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 6 }}>
                {files.map(f => (
                  <div key={f.id} style={{
                    display: 'flex', alignItems: 'center', gap: 8,
                    padding: '8px 10px', background: 'var(--bg-4)',
                    borderRadius: 8, fontSize: 12,
                  }}>
                    <FileText size={14} color="var(--accent)" />
                    <span style={{ flex: 1, color: 'var(--text-2)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {f.name}
                    </span>
                    {f.status === 'done'
                      ? <CheckCircle size={14} color="var(--green)" />
                      : (
                        <button onClick={() => removeFile(f.id)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-3)', display: 'flex' }}>
                          <X size={14} />
                        </button>
                      )
                    }
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>

        {/* JD input */}
        <Card>
          <CardHeader title="Job description" right={
            <span style={{ fontSize: 11, color: 'var(--text-3)' }}>Tempel teks bebas</span>
          } />
          <div style={{ padding: 14 }}>
            <textarea
              value={jobDescription}
              onChange={e => setJobDescription(e.target.value)}
              placeholder="Tempel job description di sini..."
              style={{
                width: '100%', minHeight: 220, resize: 'vertical',
                background: 'var(--bg-3)', border: '1px solid var(--border-2)',
                borderRadius: 8, padding: '10px 12px', fontSize: 13,
                color: 'var(--text)', lineHeight: 1.7, fontFamily: 'var(--font)',
              }}
            />

            {/* Progress */}
            {progress && (
              <div style={{ marginTop: 10 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-3)', marginBottom: 5 }}>
                  <span>{progress.label}</span>
                  <span>{progress.current}/{progress.total}</span>
                </div>
                <div style={{ height: 4, background: 'var(--bg-4)', borderRadius: 3, overflow: 'hidden' }}>
                  <div style={{
                    height: '100%', borderRadius: 3,
                    background: 'var(--accent)',
                    width: `${(progress.current / progress.total) * 100}%`,
                    transition: 'width .4s ease',
                  }} />
                </div>
              </div>
            )}

            <Btn
              variant="primary"
              style={{ marginTop: 12, width: '100%', justifyContent: 'center' }}
              onClick={handleRun}
              disabled={!canRun || running}
            >
              <Cpu size={15} />
              {running ? 'Memproses...' : 'Jalankan Screening AI'}
            </Btn>
            {!canRun && !running && (
              <div style={{ fontSize: 11, color: 'var(--text-3)', textAlign: 'center', marginTop: 6 }}>
                {!files.length ? 'Unggah minimal 1 CV terlebih dahulu' : 'Isi job description (min. 20 karakter)'}
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}
