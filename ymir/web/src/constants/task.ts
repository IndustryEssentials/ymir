import t from '@/utils/t'

export const TASKTYPES = Object.freeze({
  TRAINING: 1,
  MINING: 2,
  LABEL: 3,
  FILTER: 4,
  IMPORT: 5,
  SHARE: 6,
  PUBLIC: 7,
})

export const TASKSTATES = Object.freeze({
  UNKOWN: 0,
  PENDING: 1,
  DOING: 2,
  FINISH: 3,
  FAILURE: 4,
  TERMINATED: 100,
})

export const isFinalState = (state: number) => {
  return [TASKSTATES.FINISH, TASKSTATES.FAILURE, TASKSTATES.TERMINATED].indexOf(state) >= 0
}

export const getTaskTypeLabel = (type: number) => {

  const labels = {
    [TASKTYPES.TRAINING]: t('task.type.train'),
    [TASKTYPES.MINING]: t('task.type.mine'),
    [TASKTYPES.LABEL]: t('task.type.label'),
    [TASKTYPES.FILTER]: t('task.type.filter'),
    [TASKTYPES.IMPORT]: t('task.type.import'),
  }

  return labels[type]
}
