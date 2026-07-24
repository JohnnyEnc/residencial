export function money(v: string | number) {
  const n = typeof v === 'string' ? Number(v) : v
  return new Intl.NumberFormat('es-DO', {
    style: 'currency',
    currency: 'DOP',
    maximumFractionDigits: 0,
  }).format(n || 0)
}

export function statusLabel(s: string) {
  const map: Record<string, string> = {
    pending: 'Pendiente',
    submitted: 'En revisión',
    paid: 'Pagado',
    overdue: 'Vencido',
    open: 'Abierto',
    assigned: 'Asignado',
    in_progress: 'En proceso',
    resolved: 'Resuelto',
    closed: 'Cerrado',
    approved: 'Aprobado',
    rejected: 'Rechazado',
  }
  return map[s] || s
}

export function statusClass(s: string) {
  const map: Record<string, string> = {
    pending: 'bg-amber-100 text-amber-900',
    submitted: 'bg-lagoon-100 text-lagoon-800',
    paid: 'bg-lime/50 text-ink',
    overdue: 'bg-ember/15 text-ember',
    open: 'bg-amber-100 text-amber-900',
    assigned: 'bg-lagoon-100 text-lagoon-800',
    in_progress: 'bg-dusk/10 text-dusk',
    resolved: 'bg-lime/40 text-ink',
    closed: 'bg-mist text-lagoon-800',
    approved: 'bg-lime/50 text-ink',
    rejected: 'bg-ember/15 text-ember',
  }
  return map[s] || 'bg-mist text-lagoon-800'
}
