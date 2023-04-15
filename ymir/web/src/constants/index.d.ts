import { ResultStates } from './common'
import { STATES } from './image'
import { ObjectType } from './objectType'
import { TASKSTATES, TASKTYPES } from './task'
import { TaskResultType } from './TaskResultType'

type Matable<U> = {
  [Type in keyof U]: {
    type: Type
  } & U[Type]
}[keyof U]
type Message = Matable<M>

type M = {
  [TaskResultType.dataset]: MessageBase<YModels.Dataset>,
  [TaskResultType.model]: MessageBase<YModels.Model>,
  [TaskResultType.prediction]: MessageBase<YModels.Prediction>,
  [TaskResultType.image]: MessageBase<Image>,
}

type MessageBase<T> = {
  id: number
  pid: number
  resultId: number
  resultState: ResultStates
  taskId: number
  taskState: TASKSTATES
  taskType: TASKTYPES
  resultModule: MessageResultModules
  result?: T
}

type MessageResultModules = 'dataset' | 'model' | 'prediction' | 'image'

interface Prediction extends Omit<YModels.Dataset<YModels.InferenceParams>, 'metricLevels' | 'metrics'> {
  inferModelId: number[]
  inferModel?: YModels.Model
  inferDatasetId: number
  inferDataset?: YModels.Dataset
  inferConfig: ImageConfig
  rowSpan?: number
  evaluated: boolean
  pred: YModels.AnnotationsCount
  inferClass?: Array<string>
  odd?: boolean
}


type ImageConfig = { [key: string]: number | string }
type DockerImageConfig = {
  type: number
  config: ImageConfig
  object_type?: ObjectType
}
type Image = {
  id: number
  name: string
  state: number
  functions: number[]
  configs: DockerImageConfig[]
  objectTypes: ObjectType[]
  url: string
  description: string
  createTime: string
  official: boolean
  related?: Array<Image>
  liveCode?: boolean
  errorCode?: string
}

export { Message, MessageResultModules, Prediction, Image, DockerImageConfig }
