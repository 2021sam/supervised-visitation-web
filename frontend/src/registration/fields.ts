export const requiredFields = [
  ['first_name', 'First name'],
  ['last_name', 'Last name'],
  ['phone', 'Phone number'],
  ['zip_code', 'ZIP code'],
] as const

export const preferredFields = [
  ['professional_title', 'Professional title'],
  ['email', 'Public email address'],
  ['website', 'Website'],
  ['city', 'City'],
  ['state_code', 'State'],
  ['county', 'County'],
  ['languages', 'Languages spoken'],
  ['service_counties', 'Counties served'],
  ['service_area', 'Service area'],
  ['calendar_url', 'Calendar link'],
  ['reference_point', 'Public Reference Address'],
] as const

export const booleanFields = [
  ['phone_is_cell', 'Cell phone'],
  ['accepting_new_clients', 'Accepting new clients'],
  ['supervised_visitation', 'Supervised visitation'],
  ['supervised_exchange', 'Supervised exchange'],
  ['transportation', 'Transportation'],
  ['virtual_visitation', 'Virtual visitation'],
  ['on_site_visitation', 'On-site visitation'],
  ['off_site_visitation', 'Off-site visitation'],
  ['handwritten_reports', 'Handwritten reports'],
  ['typed_reports', 'Typed reports'],
  ['is_smoker', 'Smoker'],
  ['uses_vape', 'Vaping'],
  ['charges_roundtrip_mileage', 'Charge round-trip mileage'],
  ['charges_roundtrip_driving_time', 'Charge round-trip driving time'],
] as const
