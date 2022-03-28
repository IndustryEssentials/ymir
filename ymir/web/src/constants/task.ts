export const TASKTYPES = Object.freeze({
  TRAINING: 1,
  MINING: 2,
  LABEL: 3,
  FILTER: 4,
  IMPORT: 5,
  EXPORT: 6,
  COPY: 7,
  INFERENCE: 9,
  FUSION: 11,
  SYS: 105,
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
  return {
    [TASKTYPES.TRAINING]: 'task.type.train',
    [TASKTYPES.MINING]: 'task.type.mining',
    [TASKTYPES.LABEL]: 'task.type.label',
    [TASKTYPES.FUSION]: 'task.type.fusion',
    [TASKTYPES.COPY]: 'task.type.copy',
    [TASKTYPES.INFERENCE]: 'task.type.inference',
    [TASKTYPES.IMPORT]: 'task.type.import',
    [TASKTYPES.SYS]: 'task.type.sys',
  }[type]
}
export const getTaskStateLabel = (state: number) => {
  return {
    [TASKSTATES.PENDING]: 'task.state.pending',
    [TASKSTATES.DOING]: 'task.state.doing',
    [TASKSTATES.FINISH]: 'task.state.finish',
    [TASKSTATES.FAILURE]: 'task.state.failure',
    [TASKSTATES.TERMINATED]: 'task.state.terminated',
  }[state]
}
