export interface Supervisor {
  supervisor_id: number
  name: string
  phone: string
  email: string
  website: string
  address: string
  city: string
  state_code: string
  zip_code: string
}

export interface SupervisorResponse {
  count: number
  supervisors: Supervisor[]
}
