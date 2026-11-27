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

  latitude?: number | null
  longitude?: number | null
  service_area?: string | null
  service_zip_code?: string | null
  languages?: string | null
  service_counties?: string | null
  additional_info?: string | null

  resolved_zip_code?: string
  distance_miles?: number
  distance_basis?:
    | 'service_zip_code'
    | 'zip_code'
    | 'service_area_city'
}

export interface SupervisorResponse {
  count: number
  supervisors: Supervisor[]
}
