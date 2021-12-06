import { TASKSTATES, TASKTYPES } from '../task'

describe("constants: task", () => {
  it("have right task states, constantly and freeze.", () => {
    expect(TASKTYPES.TRAINING).toBe(1)
    expect(TASKTYPES.MINING).toBe(2)
    expect(TASKTYPES.LABEL).toBe(3)
    expect(TASKTYPES.FILTER).toBe(4)
    expect(TASKTYPES.IMPORT).toBe(5)
    expect(TASKTYPES.SHARE).toBe(6)

    function tryExtendAttr () { TASKTYPES.newAttr = 'test' }
    expect(tryExtendAttr).toThrowError('object is not extensible')
  })
  it("have right task types, constantly and freeze.", () => {
    expect(TASKSTATES.PENDING).toBe(1)
    expect(TASKSTATES.DOING).toBe(2)
    expect(TASKSTATES.FINISH).toBe(3)
    expect(TASKSTATES.FAILURE).toBe(4)

    function tryExtendAttr () { TASKSTATES.newAttr = 'test' }
    expect(tryExtendAttr).toThrowError('object is not extensible')
  })
})
