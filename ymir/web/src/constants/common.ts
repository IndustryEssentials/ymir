


import { BackendData } from "@/interface/common"
export const HIDDENMODULES = {
  VISUALIZATION: true,
  OPENPAI: true,
  LIVECODE: true,
}

export enum ResultStates {
  READY = 0,
  VALID = 1,
  INVALID = 2,
}

export enum actions {
  hide = 'hide',
  restore = 'unhide',
  del = 'delete',
}

export const OPENPAI_MAX_GPU_COUNT  = 8

type Result = {
  [key: string]: any,
}
export function updateResultState(result: Result, tasks: BackendData) {
  const task = tasks[result?.task?.hash]
  if (!result || !task) {
    return
  }
  if ([states.VALID, states.INVALID].includes(task.result_state)) {
    result.needReload = true
  }
  result.state = task.result_state
  result.progress = task.percent
  result.taskState = task.state
  result.task.state = task.state
  result.task.percent = task.percent
  return result
}

export function validState(state: number) {
  return states.VALID === state
}
