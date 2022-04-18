import { TASKSTATES, TASKTYPES, isFinalState, getTaskTypeLabel } from '../task'

describe("constants: task", () => {
  it('isFinalState', () => {
    expect(isFinalState(TASKSTATES.UNKOWN)).toBe(false)
    expect(isFinalState(TASKSTATES.PENDING)).toBe(false)
    expect(isFinalState(TASKSTATES.DOING)).toBe(false)
    expect(isFinalState(TASKSTATES.FINISH)).toBe(true)
    expect(isFinalState(TASKSTATES.FAILURE)).toBe(true)
    expect(isFinalState(TASKSTATES.TERMINATED)).toBe(true)
  })
  it('getTaskTypeLabel', () => {
    expect(getTaskTypeLabel(TASKTYPES.TRAINING)).toBe('task.type.train')
    expect(getTaskTypeLabel(TASKTYPES.MINING)).toBe('task.type.mining')
    expect(getTaskTypeLabel(TASKTYPES.LABEL)).toBe('task.type.label')
    expect(getTaskTypeLabel(TASKTYPES.FUSION)).toBe('task.type.fusion')
    expect(getTaskTypeLabel(TASKTYPES.COPY)).toBe('task.type.copy')
    expect(getTaskTypeLabel(TASKTYPES.INFERENCE)).toBe('task.type.inference')
    expect(getTaskTypeLabel(TASKTYPES.IMPORT)).toBe('task.type.import')
    expect(getTaskTypeLabel(TASKTYPES.MODELIMPORT)).toBe('task.type.modelimport')
    expect(getTaskTypeLabel(TASKTYPES.MODELCOPY)).toBe('task.type.modelcopy')
    expect(getTaskTypeLabel(TASKTYPES.SYS)).toBe('task.type.sys')
    expect(getTaskTypeLabel('not_in_task_types')).toBe('not_in_task_types')
  })
})
