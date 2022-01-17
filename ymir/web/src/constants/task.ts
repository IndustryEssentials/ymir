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
