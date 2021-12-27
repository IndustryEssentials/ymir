import { TYPES } from '../image'

describe("constants: mirror", () => {
  it("have right mapping and object is freeze", () => {
    expect(TYPES.TRAINING).toBe(1)
    expect(TYPES.MINING).toBe(2)

    function tryExtendAttr () { TYPES.newAttr = 'test' }
    expect(tryExtendAttr).toThrowError('object is not extensible')
  })
})
