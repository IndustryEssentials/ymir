import { Message, MessageResultModules, Backend } from '.'
import { TaskResultType } from './TaskResultType'

const transferMessage = (data: Backend): Message => {
  const type = data.result.type
  const msg = {
    id: data.id,
    pid: data.project_id,
    type,
    resultId: data.result.id,
    resultState: data.result.state,
    taskId: data.task_id,
    taskState: data.state,
    taskType: data.task_type,
    resultModule: resultMaps[type],
  }
  return msg
}

const resultMaps: { [key: number]: MessageResultModules } = {
  [TaskResultType.dataset]: 'dataset',
  [TaskResultType.model]: 'model',
  [TaskResultType.prediction]: 'prediction',
  [TaskResultType.image]: 'image',
}

export { transferMessage }
