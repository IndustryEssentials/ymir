import { TASKTYPES, TASKSTATES } from '../constants/task'
type DockerConfig = {
  [key: string]: string | number
}
// type WithIteration = {
//   iteration?: number
//   stage?: number
// }
type WithDocker = {
  config: DockerConfig
  image: number
}
type modelStage = [number, number | undefined | null]

type TasksQuery = {
  stages?: number[]
  datasets?: number[]
  name?: string
  type?: TASKTYPES
  state?: TASKSTATES
  start_time?: string
  end_time?: string
  offset?: number
  limit?: number
  is_desc?: boolean
  order_by?: string
}

type FusionParams = {
  project_id: number
  group_id?: number
  dataset?: number
  include_datasets?: number[]
  mining_strategy?: number
  include_strategy?: number
  exclude_result?: boolean
  exclude_datasets?: number[]
  include?: number[]
  exclude?: number[]
  samples?: number
  description?: string
}

type FilterParams = {
  projectId: number
  dataset: number
  name?: string
  includes?: number[]
  excludes?: number[]
  samples?: number
  description?: string
}

type MergeParams = {
  projectId: number
  datasets: number[]
  group?: number
  name?: string
  strategy?: number
  excludes?: number[]
  description?: string
}

type LabelParams = {
  projectId: number
  datasetId: number
  groupId?: number
  name?: string
  keywords?: string
  keepAnnotations?: boolean
  doc?: string
  description?: string
}

type TrainingParams = WithDocker & {
  projectId: number
  datasetId: number
  keywords: string[]
  testset: number
  modelStage?: modelStage
  trainType?: number
  openpai?: boolean
  strategy?: number
  description?: string
}

type MiningParams = WithDocker & {
  projectId: number
  datasetId: number
  modelStage: modelStage
  topk?: number
  name?: string
  openpai?: boolean
  description?: string
}

type InferenceParams = WithDocker & {
  projectId: number
  dataset: number[]
  stage: number[]
  name?: string
  openpai?: boolean
  description?: string
}

type TaskParams = (FusionParams | MergeParams | FilterParams | LabelParams | TrainingParams | MiningParams | InferenceParams) & {
  type: TASKTYPES
}
