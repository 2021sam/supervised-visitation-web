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

  profile_photo?: string | null
  provider_type?: string | null
  professional_title?: string | null
  reference_point?: string | null
  calendar_url?: string | null
  phone_is_cell?: number | null
  accepting_new_clients?: number | null
  supervised_visitation?: number | null
  supervised_exchange?: number | null
  transportation?: number | null
  virtual_visitation?: number | null
  on_site_visitation?: number | null
  off_site_visitation?: number | null
  handwritten_reports?: number | null
  typed_reports?: number | null
  is_smoker?: number | null
  uses_vape?: number | null
  price_per_mile?: number | null
  driving_hourly_rate?: number | null
  charges_roundtrip_mileage?: number | null
  charges_roundtrip_driving_time?: number | null

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
