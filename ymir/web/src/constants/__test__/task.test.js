import { TASKSTATES, TASKTYPES, isFinalState } from '../task'

describe("constants: task", () => {
  it("have right task states, constantly and freeze.", () => {
    expect(TASKTYPES.TRAINING).toBe(1)
    expect(TASKTYPES.MINING).toBe(2)
    expect(TASKTYPES.LABEL).toBe(3)
    expect(TASKTYPES.IMPORT).toBe(5)
    expect(TASKTYPES.COPY).toBe(7)
    expect(TASKTYPES.INFERENCE).toBe(15)
    expect(TASKTYPES.FUSION).toBe(11)

  })
  it("have right task types, constantly and freeze.", () => {
    expect(TASKSTATES.PENDING).toBe(1)
    expect(TASKSTATES.DOING).toBe(2)
    expect(TASKSTATES.FINISH).toBe(3)
    expect(TASKSTATES.FAILURE).toBe(4)

  })
  it('isFinalState', () => {
    expect(isFinalState(TASKSTATES.UNKOWN)).toBe(false)
    expect(isFinalState(TASKSTATES.PENDING)).toBe(false)
    expect(isFinalState(TASKSTATES.DOING)).toBe(false)
    expect(isFinalState(TASKSTATES.FINISH)).toBe(true)
    expect(isFinalState(TASKSTATES.FAILURE)).toBe(true)
    expect(isFinalState(TASKSTATES.TERMINATED)).toBe(true)
  })
})
