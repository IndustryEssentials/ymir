import dataset from '../dataset'
import { put, putResolve, call, select } from 'redux-saga/effects'
import { errorCode, normalReducer, product, products } from './func'
import { toFixed } from '@/utils/number'
import { transferDatasetGroup, transferDataset, transferAsset, states } from '@/constants/dataset'

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

describe('models: dataset', () => {
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
  errorCode(dataset, 'getDatasetGroups')
  errorCode(dataset, 'getDataset', { id: 120034, force: true })
  errorCode(dataset, 'batchDatasets')
  errorCode(dataset, 'delDataset')
  errorCode(dataset, 'delDatasetGroup')
  errorCode(dataset, 'createDataset')
  errorCode(dataset, 'updateDataset')
  errorCode(dataset, 'getInternalDataset')
  const gid = 534234
  const items = products(4)
  const datasets = { items, total: items.length }
  const importing = { items: [1, 2, 3, 6], max: 6 }
  normalReducer(dataset, 'UpdateDatasets', { [916]: datasets }, { [916]: datasets }, 'datasets', {})
  normalReducer(dataset, 'UpdateVersions', { [gid]: items }, { [gid]: items }, 'versions', {})
  normalReducer(dataset, 'UpdateDataset', { [gid]: product(534) }, { [gid]: product(534) }, 'dataset', {})
  normalReducer(dataset, 'UpdatePublicDatasets', datasets, datasets, 'publicDatasets', { items: [], total: 0 })
  normalReducer(dataset, 'UpdateQuery', { limit: 20 }, { limit: 20 }, 'query', {})
  normalReducer(dataset, 'UpdateTrainingDatasetCount', 15, 15, 'trainingDatasetCount', 0)
  normalReducer(dataset, 'UpdateValidDatasetCount', 18, 18, 'validDatasetCount', 0)
  normalReducer(dataset, 'UpdateImporting', importing, importing, 'importing', { items: [], max: 10 })

  it('reducers: CLEAR_ALL', () => {
    const state = {
      datasets: {},
    }
    const initQuery = { name: '', type: '', current: 1, time: 0, offset: 0, limit: 20 }

    const expected = {
      query: { ...initQuery },
      datasets: {},
      versions: {},
      dataset: {},
      allDatasets: {},
      publicDatasets: [],
      trainingDatasetCount: 0,
      validDatasetCount: 0,
      importing: {
        items: [],
        max: 10,
      },
    }
    const action = {
      payload: null,
    }
    const result = dataset.reducers.CLEAR_ALL(state, action)
    expect(result).toEqual(expected)
  })

  it('effects: UpdateImporting', () => {
    const list = [1, 2, 34, 65]
    const expected = { items: list, max: 6 }
    const action = {
      payload: expected,
    }
    const { importing } = dataset.effects.UpdateImporting(state, action)
    expect(importing).toEqual(expected)
  })

  it('effects: getDatasetGroups', () => {
    const saga = dataset.effects.getDatasetGroups
    const pid = 134324
    const creator = {
      type: 'getDatasetGroups',
      payload: { pid },
    }
    const datetime = '2022-02-14T10:03:49'
    const origin = [1, 2, 3, 4].map((item) => {
      return {
        id: item,
        pid,
        name: 'name' + item,
        create_datetime: datetime,
      }
    })
    const recieved = origin.map((item) => transferDatasetGroup(item))
    const expected = { items: recieved, total: recieved.length }

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: { items: origin, total: origin.length },
    })
    let end = {}
    generator.next()
    for (let index = 0; index < recieved.length; index++) {
      if (index === recieved.length - 1) {
        end = generator.next()
      } else {
        generator.next()
      }
    }

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it('effects: getDataset', () => {
    const saga = dataset.effects.getDataset
    const creator = {
      type: 'getDataset',
      payload: { gid: 10002 },
    }
    const recieved = ds(1)
    const expected = transferDataset(recieved)

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
  it('effects: batchDatasets', () => {
    const saga = dataset.effects.batchDatasets
    const creator = {
      type: 'batchDatasets',
      payload: { pid: 23434, ids: [1, 2] },
    }
    const recieved = [1, 3, 4].map((id) => ds(id))
    const expected = recieved.map((item) => transferDataset(item))

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: recieved,
    })
    const end = generator.next()

    expect(expected).toEqual(end.value)
    expect(end.done).toBe(true)
  })
  it('effects: queryAllDatasets -> from remote', () => {
    const saga = dataset.effects.queryAllDatasets
    const creator = {
      type: 'queryAllDatasets',
      payload: { pid: 132223, force: true },
    }
    const expected = { items: [1, 2, 3, 4], total: 4 }

    const generator = saga(creator, { put, call, select })
    generator.next()
    generator.next(false)
    generator.next(expected)
    const end = generator.next()

    expect(end.value).toEqual(expected.items)
    expect(end.done).toBe(true)
  })
  it('effects: queryAllDatasets -> from cache success', () => {
    const saga = dataset.effects.queryAllDatasets
    const creator = {
      type: 'queryAllDatasets',
      payload: { pid: 132223 },
    }
    const expected = [1, 2, 3, 4]

    const generator = saga(creator, { put, call, select })
    generator.next()
    generator.next(false)
    const end = generator.next(expected)

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it('effects: queryAllDatasets -> from remote when cache failed.', () => {
    const saga = dataset.effects.queryAllDatasets
    const creator = {
      type: 'queryAllDatasets',
      payload: { pid: 132223 },
    }
    const expected = [1, 2, 3, 4]

    const generator = saga(creator, { put, call, select })
    generator.next()
    generator.next(false)
    generator.next([])
    generator.next({ items: expected, total: expected.length })
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it('effects: getDatasetVersions -> success from cache.', () => {
    const saga = dataset.effects.getDatasetVersions
    const gid = 134234
    const creator = {
      type: 'getDatasetVersions',
      payload: { gid },
    }
    const items = products(4).map((id) => ds(id))
    const expected = items.map((item) => transferDataset(item))

    const generator = saga(creator, { put, call, select })
    generator.next()
    const end = generator.next({ [gid]: expected })

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it('effects: getDatasetVersions -> cache failed, and success from remote.', () => {
    const saga = dataset.effects.getDatasetVersions
    const gid = 134234
    const creator = {
      type: 'getDatasetVersions',
      payload: { gid },
    }
    const items = products(4).map((id) => ds(id))
    const expected = items.map((item) => transferDataset(item))

    const generator = saga(creator, { put, call, select })
    generator.next()
    generator.next({})
    generator.next({ code: 0, result: { items, total: items.length } })
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it('effects: getDatasetVersions -> success from remote.', () => {
    const saga = dataset.effects.getDatasetVersions
    const gid = 134234
    const creator = {
      type: 'getDatasetVersions',
      payload: { gid, force: true },
    }
    const items = products(4).map((id) => ds(id))
    const expected = items.map((item) => transferDataset(item))

    const generator = saga(creator, { put, call, select })
    generator.next()
    generator.next({ code: 0, result: { items, total: items.length } })
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it('effects: delDatasetGroup -> success', () => {
    const saga = dataset.effects.delDatasetGroup
    const id = 133445
    const creator = {
      type: 'delDatasetGroup',
      payload: { id },
    }
    const expected = { id, name: 'del group' }

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it('effects: delDataset', () => {
    const saga = dataset.effects.delDataset
    const creator = {
      type: 'delDataset',
      payload: { id: 10001 },
    }
    const expected = { id: 10001, name: 'del_dataset_name' }

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it('effects: createDataset', () => {
    const saga = dataset.effects.createDataset
    const expected = { id: 10001, name: 'new_dataset_name' }
    const creator = {
      type: 'createDataset',
      payload: { id: 10001, name: 'new_dataset_name', type: 1 },
    }

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it('effects: updateDataset', () => {
    const saga = dataset.effects.updateDataset
    const creator = {
      type: 'updateDataset',
      payload: { id: 10001, name: 'new_dataset_name' },
    }
    const expected = { id: 10001, name: 'new_dataset_name' }

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    equalObject(expected, end.value)
    expect(end.done).toBe(true)
  })
  it('effects: updateDatasets -> normal success', () => {
    const saga = dataset.effects.updateDatasets
    const ds = (id, state, result_state, progress) => ({
      id,
      task: { hash: `hash${id}`, state, percent: progress },
      taskState: state,
      state: result_state,
      progress,
    })

    const versions = {
      34: [ds(1, 2, 0, 0.2), ds(2, 3, 1, 1), ds(3, 3, 1, 1)],
      35: [ds(4, 3, 1, 1), ds(5, 3, 1, 1), ds(6, 3, 1, 1)],
      36: [ds(7, 2, 0, 0.96), ds(8, 3, 1, 1)],
    }
    const creator = {
      type: 'updateDatasets',
      payload: { hash1: { id: 1, state: 2, result_state: 0, percent: 0.45 }, hash7: { id: 7, state: 3, result_state: 1, percent: 1 } },
    }
    const expected = {
      34: [ds(1, 2, 0, 0.45), ds(2, 3, 1, 1), ds(3, 3, 1, 1)],
      35: [ds(4, 3, 1, 1), ds(5, 3, 1, 1), ds(6, 3, 1, 1)],
      36: [{ ...ds(7, 3, 1, 1), needReload: true }, ds(8, 3, 1, 1)],
    }

    const generator = saga(creator, { put, call, select })
    generator.next()
    const d = generator.next(versions)
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it('effects: updateDatasets -> empty success', () => {
    const saga = dataset.effects.updateDatasets
    const ds = (id, state, result_state, progress) => ({ id, task: { hash: `hash${id}` }, result_state, state, progress })
    const versions = {
      34: [ds(1, 2, 0.2), ds(2, 3, 1), ds(3, 3, 1)],
      35: [ds(4, 3, 1), ds(5, 3, 1), ds(6, 3, 1)],
      36: [ds(7, 2, 0.96), ds(8, 3, 1)],
    }
    const creator = {
      type: 'updateDatasets',
    }

    const generator = saga(creator, { put, call, select })
    generator.next()
    const d = generator.next(versions)
    const end = generator.next()

    expect(end.value).toEqual(versions)
    expect(end.done).toBe(true)
  })
  it('effects: updateDatasetState -> normal success', () => {
    const saga = dataset.effects.updateDatasetState
    const ds = (id, state, result_state, progress) => ({
      id,
      task: { hash: `hash${id}`, state, percent: progress },
      taskState: state,
      state: result_state,
      progress,
    })

    const datasets = {
      1: ds(1, 2, 0, 0.2),
    }
    const creator = {
      type: 'updateDatasets',
      payload: {
        hash1: { id: 1, state: 2, result_dataset: { id: 1 }, result_state: 0, percent: 0.45 },
        hash7: { id: 7, state: 3, result_state: 1, percent: 1 },
      },
    }
    const expected = {
      1: ds(1, 2, 0, 0.45),
    }

    const generator = saga(creator, { put, call, select })
    generator.next()
    const d = generator.next(datasets)
    const end = generator.next()
    expect(end.done).toBe(true)
  })
  it('effects: getInternalDataset', () => {
    const saga = dataset.effects.getInternalDataset
    const creator = {
      type: 'getInternalDataset',
      payload: {},
    }
    const recieved = [1, 3, 4, 5, 6].map((id) => ds(id))
    const expected = { items: recieved.map((item) => transferDataset(item)), total: recieved.length }

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: { items: recieved, total: recieved.length },
    })
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it('effects: getValidDatasetsCount', () => {
    const saga = dataset.effects.getValidDatasetsCount
    const pid = 63343
    const creator = {
      type: 'getValidDatasetsCount',
      payload: pid,
    }
    const total = 3
    const result = { items: products(total), total }
    const generator = saga(creator, { put })
    generator.next()
    generator.next(result)
    const end = generator.next()

    expect(end.value).toBe(total)
  })

  it('effects: getTrainingDatasetCount', () => {
    const saga = dataset.effects.getTrainingDatasetCount
    const pid = 63343
    const creator = {
      type: 'getTrainingDatasetCount',
      payload: pid,
    }
    const total = 4
    const result = { items: products(total), total }
    const generator = saga(creator, { put })
    generator.next()
    generator.next(result)
    const end = generator.next()

    expect(end.value).toBe(total)
  })
})
