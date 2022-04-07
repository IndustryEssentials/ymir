


import { BackendData } from "@/interface/common"
import { TASKSTATES } from "./task"
export enum states {
  READY = 0,
  VALID = 1,
  INVALID = 2,
}

export const getResultStateFromTask = (taskState: TASKSTATES) => {
  const maps = {
    [TASKSTATES.DOING]: states.READY,
    [TASKSTATES.PENDING]: states.READY,
    [TASKSTATES.FINISH]: states.VALID,
    [TASKSTATES.FAILURE]: states.INVALID,
    [TASKSTATES.TERMINATED]: states.VALID,
  }
  return maps[taskState]
}

type Result = {
  [key: string]: any,
}
export function updateResultState(result: Result, tasks: BackendData) {
  const task = tasks[result?.task?.hash]
  if (task) {
    if ([states.VALID, states.INVALID].includes(task.result_state)) {
      result.needReload = true
    }
    result.state = task.result_state
    result.progress = task.percent
    result.taskState = task.state
    result.task.state = task.state
    result.task.percent = task.percent
  }
  return result
}