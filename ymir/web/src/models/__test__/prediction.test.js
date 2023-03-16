import prediction from '../prediction'
import { put, putResolve, call, select } from 'redux-saga/effects'
import { errorCode, normalReducer, product, products, list } from './func'
import { toFixed } from '@/utils/number'
import { transferPrediction } from '@/constants/prediction'

jest.mock('umi', () => {
  return {
    getLocale() {
      return 'en-US'
    },
  }
})

put.resolve = putResolve

function equalObject(obj1, obj2) {
  expect(JSON.stringify(obj1)).toBe(JSON.stringify(obj2))
}

describe('models: prediction', () => {
  const createTime = '2022-03-10T03:39:09'
  const task = {
    name: 't00000020000013277a01646883549',
    type: 105,
    project_id: 1,
    is_deleted: false,
    create_datetime: createTime,
    update_datetime: createTime,
    id: 1,
    hash: 't00000020000013277a01646883549',
    state: 3,
    error_code: null,
    duration: null,
    percent: 1,
    parameters: {},
    config: {},
    user_id: 2,
    last_message_datetime: '2022-03-10T03:39:09.033206',
    is_terminated: false,
    result_type: null,
  }

  const ds = (id) => ({
    name: 'p0001_training_dataset',
    result_state: 1,
    dataset_group_id: 1,
    state: 1,
    keywords: {},
    ignored_keywords: {},
    asset_count: null,
    keyword_count: null,
    is_deleted: false,
    create_datetime: createTime,
    update_datetime: createTime,
    id: id,
    hash: 't00000020000012afef21646883528',
    version_num: 0,
    task_id: 1,
    user_id: 2,
    related_task: task,
  })

  const generateItems = (mids, isExpected) => {
    const item = (curr, exp, listIndex) => ({id}, index) => exp ? { ...transferPrediction(ds(id)), rowSpan: index ? 0 : curr, odd: listIndex % 2 === 0 } : ds(id)
    const items = mids.reduce((prev, curr, index) => ({ ...prev, [curr]: products(curr).map(item(curr, isExpected, index)) }), {})
    const total = mids.length
    return { items: isExpected ? Object.values(items).flat() : items, total }
  }

  errorCode(prediction, 'getPrediction', { id: 120034, force: true })
  const pid = 534234
  const items = products(4)
  const predictions = { items, total: items.length }
  normalReducer(prediction, 'UpdatePredictions', predictions, predictions, 'predictions', { items: [], total: 0 })
  normalReducer(prediction, 'UpdatePrediction', { [pid]: product(634) }, { [pid]: product(634) }, 'prediction', {})

  it('effects: getPrediction', () => {
    const saga = prediction.effects.getPrediction
    const creator = {
      type: 'getPrediction',
      payload: { pid: 10002 },
    }
    const recieved = ds(1)
    const expected = transferPrediction(recieved)

    const generator = saga(creator, { put, call, select })
    generator.next()
    generator.next()
    const calls = generator.next({
      code: 0,
      result: recieved,
    })
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it('effects: getPredictions -> success from cache.', () => {
    const saga = prediction.effects.getPredictions
    const pid = 134234
    const mids = [1,2,5]
    const creator = {
      type: 'getPredictions',
      payload: { pid },
    }
    const expected = generateItems(mids, true)

    const generator = saga(creator, { put, call, select })
    generator.next()
    const end = generator.next(expected)

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it('effects: getPredictions -> cache failed, and success from remote.', () => {
    const saga = prediction.effects.getPredictions
    const pid = 134234
    const mids = [1, 2, 3]
    const creator = {
      type: 'getPredictions',
      payload: { pid },
    }
    const result = generateItems(mids)
    const expected = generateItems(mids, true)

    const generator = saga(creator, { put, call, select })
    generator.next()
    generator.next(null)
    generator.next({ code: 0, result })
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it('effects: getPredictions -> success from remote.', () => {
    const saga = prediction.effects.getPredictions
    const pid = 134234
    const mids = [1, 3, 4]
    const creator = {
      type: 'getPredictions',
      payload: { pid, force: true },
    }
    const result = generateItems(mids)
    const expected = generateItems(mids, true)

    const generator = saga(creator, { put, call, select })
    generator.next()
    generator.next({ code: 0, result })
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })

  it('effects: evaluate', () => {
    const saga = prediction.effects.evaluate
    const item = () => ({ ap: Math.random() })
    const list = (list, it) => list.reduce((p, c) => ({ ...p, [c]: it ? it : item() }), {})
    const keywords = ['dog', 'cat', 'person']
    const ious = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95].map((n) => toFixed(n, 2))
    const iitems = () => ({
      ci_evaluations: list(keywords),
      ci_everage_evaluations: item(),
    })
    const expected = {
      iou_evaluations: list(ious, iitems()),
      iou_everage_evaluations: iitems(),
    }
    const creator = {
      type: 'evaluate',
      payload: { pid: 51234, gt: 1324536, predictions: [534243234, 64311234], confidence: 0.6 },
    }

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    equalObject(expected, end.value)
    expect(end.done).toBe(true)
  })
})
