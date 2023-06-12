import { ResultStates } from '../common'
import { TASKSTATES, TASKTYPES } from '../task'
import { TaskResultType } from '../TaskResultType'
import { Matable } from './common'
import { Dataset } from './dataset'
import { Image } from './image'
import { Model } from './model'
import { Prediction } from './prediction'

type Message = Matable<M>

type M = {
  [TaskResultType.dataset]: MessageBase<Dataset>
  [TaskResultType.model]: MessageBase<Model>
  [TaskResultType.prediction]: MessageBase<Prediction>
  [TaskResultType.image]: MessageBase<Image>
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

export { Message, MessageResultModules }
