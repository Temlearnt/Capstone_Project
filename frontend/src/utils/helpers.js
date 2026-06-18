export function getScoreColor(score) {
  if (score >= 85) return 'var(--green)';
  if (score >= 70) return 'var(--amber)';
  return 'var(--red)';
}

export function getStatusClass(status) {
  if (status === 'Sangat Cocok') return 'badge-green';
  if (status === 'Cocok') return 'badge-amber';
  return 'badge-red';
}

export function getStatusFromScore(score) {
  if (score >= 85) return 'Sangat Cocok';
  if (score >= 65) return 'Cocok';
  return 'Perlu Review';
}
