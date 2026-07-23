export type UserRole = 'admin' | 'resident' | 'staff'

export interface UnitBrief {
  id: number
  code: string
  block: string | null
  number: string
}

export interface User {
  id: number
  email: string
  name: string
  phone: string | null
  role: UserRole
  active: boolean
  created_at: string
  units: UnitBrief[]
}

export interface Unit {
  id: number
  code: string
  block: string | null
  number: string
  floor: string | null
  status: string
  created_at: string
  members: {
    id: number
    user_id: number
    user_name: string
    user_email: string
    relation: string
  }[]
}

export interface FeePeriod {
  id: number
  year: number
  month: number
  amount_default: string
  due_date: string
  label: string | null
  created_at: string
}

export interface UnitCharge {
  id: number
  unit_id: number
  unit_code: string
  period_id: number
  period_label: string
  amount: string
  status: 'pending' | 'submitted' | 'paid' | 'overdue'
  created_at: string
}

export interface Payment {
  id: number
  charge_id: number
  amount: string
  method: string | null
  proof_url: string | null
  submitted_by: number | null
  submitted_at: string
  reviewed_by: number | null
  reviewed_at: string | null
  status: 'submitted' | 'approved' | 'rejected'
  note: string | null
}

export interface Report {
  id: number
  unit_id: number | null
  unit_code: string | null
  created_by: number
  creator_name: string | null
  assigned_to: number | null
  assignee_name: string | null
  category: string
  title: string
  description: string
  location: string | null
  photo_url: string | null
  status: string
  created_at: string
  updated_at: string
  updates: {
    id: number
    report_id: number
    author_id: number
    note: string
    status_to: string | null
    created_at: string
  }[]
}

export interface Announcement {
  id: number
  title: string
  body: string
  priority: string
  published_at: string
  expires_at: string | null
  created_by: number
  read: boolean
}

export interface DashboardStats {
  total_units: number
  total_residents: number
  total_staff: number
  open_reports: number
  collection_rate: number
  paid_amount: string
  pending_amount: string
  overdue_amount: string
  submitted_amount: string
  charges_by_status: { status: string; count: number; amount: string }[]
  paid_units: {
    unit_id: number
    unit_code: string
    amount: string
    status: string
    resident_name: string | null
  }[]
  unpaid_units: {
    unit_id: number
    unit_code: string
    amount: string
    status: string
    resident_name: string | null
  }[]
  monthly_collection: {
    year: number
    month: number
    label: string
    paid: string
    pending: string
    overdue: string
    submitted: string
  }[]
  reports_by_status: { status: string; count: number }[]
  pending_payment_reviews: number
}
