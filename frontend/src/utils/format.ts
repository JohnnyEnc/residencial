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
    pending: 'bg-amber-100 text-amber-800',
    submitted: 'bg-sky-100 text-sky-800',
    paid: 'bg-emerald-100 text-emerald-800',
    overdue: 'bg-red-100 text-red-800',
    open: 'bg-amber-100 text-amber-800',
    assigned: 'bg-sky-100 text-sky-800',
    in_progress: 'bg-indigo-100 text-indigo-800',
    resolved: 'bg-emerald-100 text-emerald-800',
    closed: 'bg-slate-100 text-slate-700',
    approved: 'bg-emerald-100 text-emerald-800',
    rejected: 'bg-red-100 text-red-800',
  }
  return map[s] || 'bg-slate-100 text-slate-700'
}
