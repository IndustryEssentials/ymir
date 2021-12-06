import { CONFIGTYPES } from '../mirror'

describe("constants: mirror", () => {
  it("have right mapping and object is freeze", () => {
    expect(CONFIGTYPES.TRAINING).toBe(1)
    expect(CONFIGTYPES.MINING).toBe(2)

    function tryExtendAttr () { CONFIGTYPES.newAttr = 'test' }
    expect(tryExtendAttr).toThrowError('object is not extensible')
  })
})
