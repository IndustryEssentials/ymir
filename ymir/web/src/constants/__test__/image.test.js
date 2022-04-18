import { TYPES, STATES, imageIsPending, getImageTypeLabel, getImageStateLabel } from '../image'

describe("constants: image", () => {
  it("image type have right mapping and object is freeze", () => {
    expect(TYPES.TRAINING).toBe(1)
    expect(TYPES.MINING).toBe(2)
    expect(TYPES.UNKOWN).toBe(0)
    expect(TYPES.INFERENCE).toBe(9)

    function tryExtendAttr () { TYPES.newAttr = 'test' }
    expect(tryExtendAttr).toThrowError('object is not extensible')
  })
  it("image states have right mapping and object is freeze", () => {
    expect(STATES.PENDING).toBe(1)
    expect(STATES.DONE).toBe(3)
    expect(STATES.ERROR).toBe(4)

    function tryExtendAttr () { STATES.newAttr = 'test' }
    expect(tryExtendAttr).toThrowError('object is not extensible')
  })
  it('imageIsPending: image state is pending', () => {

    expect(imageIsPending(STATES.PENDING)).toBe(true)
    expect(imageIsPending(STATES.DONE)).toBe(false)
    expect(imageIsPending(STATES.ERROR)).toBe(false)
    expect(imageIsPending()).toBe(false) // undefined
    expect(imageIsPending('1')).toBe(false) // type
  })
  it('getImageTypeLabel: get label by match type', () => {
    const trainLabel = getImageTypeLabel([TYPES.TRAINING])
    const miningLabel = getImageTypeLabel([TYPES.MINING])
    const inferenceLabel = getImageTypeLabel([TYPES.TRAINING, TYPES.INFERENCE])
    const emptyLabel = getImageTypeLabel()
    const unmatchLabel = getImageTypeLabel(['34'])

    expect(trainLabel).toEqual(['image.type.train'])
    expect(miningLabel).toEqual(['image.type.mining'])
    expect(inferenceLabel).toEqual(['image.type.train','image.type.inference'])
    expect(emptyLabel).toEqual([])
    expect(unmatchLabel).toEqual([undefined])

  })
  it('getImageStateLabel: get label by match state', () => {
    const pendingLabel = getImageStateLabel(STATES.PENDING)
    const doneLabel = getImageStateLabel(STATES.DONE)
    const errorLabel = getImageStateLabel(STATES.ERROR)
    const emptyLabel = getImageStateLabel()
    const unmatchLabel = getImageStateLabel('34')

    expect(pendingLabel).toBe('image.state.pending')
    expect(doneLabel).toBe('image.state.done')
    expect(errorLabel).toBe('image.state.error')
    expect(emptyLabel).toBe('')
    expect(unmatchLabel).toBe(undefined)
  })
})
