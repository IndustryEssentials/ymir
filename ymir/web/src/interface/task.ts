

export interface Task {
  name: string,
  type: number,
  project_id: number,
  is_deleted: number,
  create_datetime: string,
  update_datetime: string,
  id: number,
  hash: string,
  state: number,
  error_code: number,
  duration: number,
  percent: number,
  parameters: object,
  config: object,
  result_type: number,
}
