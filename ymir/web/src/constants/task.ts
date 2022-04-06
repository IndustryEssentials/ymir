import { states } from './dataset'

export enum TASKTYPES {
  TRAINING = 1,
  MINING = 2,
  LABEL = 3,
  IMPORT = 5,
  COPY = 7,
  INFERENCE = 9,
  FUSION = 11,
  MODELIMPORT = 13,
  MODELCOPY = 14,
  SYS = 105,
}

export enum TASKSTATES {
  PENDING = 1,
  DOING = 2,
  FINISH = 3,
  FAILURE = 4,
  TERMINATED = 100,
}

export const isFinalState = (state: TASKSTATES) => {
  return [TASKSTATES.FINISH, TASKSTATES.FAILURE, TASKSTATES.TERMINATED].includes(state)
}

export const getTaskTypeLabel = (type: TASKTYPES) => {
  const maps = {
    [TASKTYPES.TRAINING]: 'task.type.train',
    [TASKTYPES.MINING]: 'task.type.mining',
    [TASKTYPES.LABEL]: 'task.type.label',
    [TASKTYPES.FUSION]: 'task.type.fusion',
    [TASKTYPES.COPY]: 'task.type.copy',
    [TASKTYPES.INFERENCE]: 'task.type.inference',
    [TASKTYPES.IMPORT]: 'task.type.import',
    [TASKTYPES.MODELIMPORT]: 'task.type.modelimport',
    [TASKTYPES.MODELCOPY]: 'task.type.modelcopy',
    [TASKTYPES.SYS]: 'task.type.sys',
  }
  return maps[type] ? maps[type] : type
}
export const getTaskStateLabel = (state: TASKSTATES) => {
  return {
    [TASKSTATES.PENDING]: 'task.state.pending',
    [TASKSTATES.DOING]: 'task.state.doing',
    [TASKSTATES.FINISH]: 'task.state.finish',
    [TASKSTATES.FAILURE]: 'task.state.failure',
    [TASKSTATES.TERMINATED]: 'task.state.terminated',
  }[state]
}

export const getResultStateFromTask = (taskState: TASKSTATES) => {
  const maps = {
    [TASKSTATES.DOING]: states.READY,
    [TASKSTATES.PENDING]: states.READY,
    [TASKSTATES.FINISH]: states.VALID,
    [TASKSTATES.FAILURE]: states.INVALID,
    [TASKSTATES.TERMINATED]: states.VALID,
  }
  console.log('maps[taskState]:', maps, taskState)
  return maps[taskState]
}
