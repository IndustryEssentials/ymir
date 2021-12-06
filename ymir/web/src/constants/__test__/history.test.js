import { HISTORYNODETYPES } from "../history"

describe("constants: history", () => {
  it("have right history node type, freeze object.", () => {
    expect(HISTORYNODETYPES.DATASET).toBe(1)
    expect(HISTORYNODETYPES.MODEL).toBe(2)

    function tryExtendAttr () { HISTORYNODETYPES.newAttr = 'test' }
    expect(tryExtendAttr).toThrowError('object is not extensible')
  })
})
