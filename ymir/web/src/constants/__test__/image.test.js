import { format } from '@/utils/date'
import { TYPES, STATES, imageIsPending, getImageTypeLabel, getImageStateLabel, transferImage } from '../image'

describe("constants: image", () => {
  it("image type have right mapping", () => {
    expect(TYPES.TRAINING).toBe(1)
    expect(TYPES.MINING).toBe(2)
    expect(TYPES.UNKOWN).toBe(0)
    expect(TYPES.INFERENCE).toBe(9)
  })
  it("image states have right mapping", () => {
    expect(STATES.PENDING).toBe(1)
    expect(STATES.DONE).toBe(3)
    expect(STATES.ERROR).toBe(4)
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
    expect(inferenceLabel).toEqual(['image.type.train', 'image.type.inference'])
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
  it('transferImage: transfer image from backend data', () => {
    const config = (id, type) => ({
      image_id: id,
      config: {
        expected_map: 0.983,
        idle_seconds: 60,
        trigger_crash: 0,
        type: 1
      },
      type
    })
    const createTime = "2022-03-10T03:39:09"
    const functions = [1, 2, 9]
    const configs = functions.map(conf => config(1, conf))
    const backendData = {
      name: "sample_image",
      state: 3,
      hash: "f3da055bacc7",
      url: "sample-tmi:stage-test-01",
      description: "test",
      is_deleted: false,
      create_datetime: createTime,
      id: 1,
      is_shared: false,
      related: [],
      configs,
    }
    const image = transferImage(backendData)
    const expected = {
      configs,
      createTime: format(createTime),
      description: "test",
      functions, 
      liveCode: undefined,
      id: 1,
      isShared: false,
      name: "sample_image",
      related: [],
      state: 3,
      url: "sample-tmi:stage-test-01",
    }
    expect(image).toEqual(expected)
  })
})
