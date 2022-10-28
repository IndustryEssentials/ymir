type PlainObject = {
  [key: string]: any,
}

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
  parameters: Parameters,
  config: PlainObject,
  result_type: number,
  is_terminated: boolean,
}

type MergeStrategy = 0 | 1 | 2
type Preprocess = {
  [func: string]: PlainObject,
}

interface Parameters {
  dataset_id?: number,
  keywords?: string[],
  extra_url?: string,
  labellers?: string[],
  annotation_type?: number,
  validation_dataset_id?: number,
  network?: string,
  backbone?: string,
  hyperparameter?: string,
  strategy?: MergeStrategy,
  preprocess?: Preprocess,
  model_id?: number,
  model_stage_id?: number,
  mining_algorithm?: string,
  top_k?: number,
  generate_annotations?: boolean,
  docker_image?: string,
  docker_image_id?: number,
}
