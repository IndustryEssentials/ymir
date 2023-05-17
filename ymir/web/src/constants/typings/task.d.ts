import { MERGESTRATEGY } from '../dataset'
import { MiningStrategy } from '../iteration'
import { TASKSTATES, TASKTYPES } from '../task'
import { Classes } from './class'
import { Backend, Matable } from './common'
import { ImageConfig } from './image'

type TaskBase<P = Params> = {
  name: string
  project_id: number
  create_datetime: string
  update_datetime: string
  id: number
  hash: string
  state: TASKSTATES
  error_code: string
  duration: number
  percent: number
  parameters: P
  config: ImageConfig
  is_terminated: boolean
  result_type: number
}

type ParamsByType = {
  [TASKTYPES.TRAINING]: TaskBase<TrainingParams>
  [TASKTYPES.MINING]: TaskBase<MiningParams>
  [TASKTYPES.LABEL]: TaskBase<LabelParams>
  [TASKTYPES.FILTER]: TaskBase<FilterParams>
  [TASKTYPES.IMPORT]: TaskBase
  [TASKTYPES.COPY]: TaskBase
  [TASKTYPES.MERGE]: TaskBase<MergeParams>
  [TASKTYPES.INFERENCE]: TaskBase<InferenceParams>
  [TASKTYPES.FUSION]: TaskBase<FusionParams>
  [TASKTYPES.MODELIMPORT]: TaskBase
  [TASKTYPES.MODELCOPY]: TaskBase
  [TASKTYPES.IMAGEIMPORT]: TaskBase
  [TASKTYPES.SYS]: TaskBase
}

type Task = Matable<ParamsByType>

interface Params {
  dataset_id: number
  dataset_group_id?: number
  dataset_group_name?: string
  description?: string
}

interface DockerParams extends Params {
  docker_image_id: number
  docker_image_config: ImageConfig
  labels: Classes
  model_id?: number
  model_stage_id?: number
  gpuCount?: number
  config?: Backend
}

interface FilterParams extends Params {
  include_labels?: Classes
  exclude_labels?: Classes
  sampling_count?: number
}
interface FusionParams extends Params {
  iteration_id?: number
  iteration_stage?: number
  exclude_last_result?: boolean
  include_datasets?: number[]
  exclude_datasets?: number[]
  mining_strategy?: MiningStrategy
  merge_strategy?: MERGESTRATEGY
  include_labels?: Classes
  exclude_labels?: Classes
  sampling_count?: number
}

interface MergeParams extends Params {
  include_datasets?: number[]
  exclude_datasets?: number[]
  merge_strategy?: MERGESTRATEGY
}

interface LabelParams extends Params {
  labels: Classes
  extra_url?: string
  annotation_type: 1 | 2
}

interface TrainingParams extends DockerParams {
  validation_dataset_id: number
  strategy: number
}

interface MiningParams extends DockerParams {
  top_k: number
  generate_annotations?: boolean
}

interface InferenceParams extends DockerParams {}

type ProgressTask = {
  hash: string
  result_state: number
  percent: number
  state: number
  reload?: boolean
  result_dataset?: { id: number }
  result_model?: { id: number }
  result_prediction?: { id: number }
  result_image?: { id: number }
}

export { Task, ProgressTask, ParamsByType }
