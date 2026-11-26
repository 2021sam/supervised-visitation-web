export interface County {
  geoid: string
  state_code: string
  county_name: string
}

export interface CountyResponse {
  count: number
  counties: County[]
}
