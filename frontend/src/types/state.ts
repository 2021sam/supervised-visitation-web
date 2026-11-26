export interface State {
  state_name: string
  state_code: string
  flag_url: string
}

export interface StateResponse {
  count: number
  states: State[]
}
