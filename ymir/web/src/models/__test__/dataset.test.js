import dataset from "../dataset"
import { put, putResolve, call, select } from "redux-saga/effects"
import { errorCode } from './func'
import { format } from '@/utils/date'
import { transferDatasetGroup, transferDataset, states } from '@/constants/dataset'

jest.mock('umi', () => {
  return {
    getLocale() {
      return 'en-US'
    }
  }
})

put.resolve = putResolve

function equalObject(obj1, obj2) {
  expect(JSON.stringify(obj1)).toBe(JSON.stringify(obj2))
}

describe("models: dataset", () => {
  
  const createTime = "2022-03-10T03:39:09"
  const task = {
    "name": "t00000020000013277a01646883549",
    "type": 105,
    "project_id": 1,
    "is_deleted": false,
    "create_datetime": createTime,
    "update_datetime": createTime,
    "id": 1,
    "hash": "t00000020000013277a01646883549",
    "state": 3,
    "error_code": null,
    "duration": null,
    "percent": 1,
    "parameters": {},
    "config": {},
    "user_id": 2,
    "last_message_datetime": "2022-03-10T03:39:09.033206",
    "is_terminated": false,
    "result_type": null
  }

  const ds = id => ({
    "name": "p0001_training_dataset",
    "result_state": 1,
    "dataset_group_id": 1,
    state: 1,
    "keywords": {},
    "ignored_keywords": {},
    "asset_count": null,
    "keyword_count": null,
    "is_deleted": false,
    "create_datetime": createTime,
    "update_datetime": createTime,
    "id": id,
    "hash": "t00000020000012afef21646883528",
    "version_num": 0,
    "task_id": 1,
    "user_id": 2,
    "related_task": task,
  })
  errorCode(dataset, 'getDatasetGroups')
  errorCode(dataset, 'getDataset')
  errorCode(dataset, 'batchDatasets')
  errorCode(dataset, 'getAssetsOfDataset')
  errorCode(dataset, 'getAsset')
  errorCode(dataset, 'delDataset')
  errorCode(dataset, 'createDataset')
  errorCode(dataset, 'updateDataset')
  errorCode(dataset, 'getInternalDataset')
  errorCode(dataset, 'getHotDatasets', [])

  it("reducers: UPDATE_DATASETS", () => {
    const state = {
      datasets: {},
    }
    const expected = { items: [1, 2, 3, 4], total: 4 }
    const action = {
      payload: expected,
    }
    const result = dataset.reducers.UPDATE_DATASETS(state, action)
    expect(result.datasets.total).toBe(expected.total)
  })
  it("reducers: UPDATE_DATASET", () => {
    const state = {
      dataset: {},
    }
    const expected = { id: 1001 }
    const action = {
      payload: expected,
    }
    const result = dataset.reducers.UPDATE_DATASET(state, action)
    expect(result.dataset[expected.id].id).toBe(expected.id)
  })
  it("reducers: UPDATE_ASSETS", () => {
    const state = {
      assets: {},
    }
    const expected = { items: [1, 2, 3, 4], total: 4 }
    const action = {
      payload: expected,
    }
    const result = dataset.reducers.UPDATE_ASSETS(state, action)
    expect(result.assets.total).toBe(expected.total)
  })
  it("reducers: UPDATE_ASSET", () => {
    const state = {
      asset: {},
    }
    const expected = { hash: 'test' }
    const action = {
      payload: expected,
    }
    const result = dataset.reducers.UPDATE_ASSET(state, action)
    expect(result.asset.hash).toBe(expected.hash)
  })
  it("reducers: UPDATE_PUBLICDATASETS", () => {
    const state = {
      publicDatasets: [],
    }
    const expected = [1, 2, 3, 4]
    const action = {
      payload: expected,
    }
    const result = dataset.reducers.UPDATE_PUBLICDATASETS(state, action)
    expect(result.publicDatasets.join(',')).toBe(expected.join(','))
  })

  it("effects: getDatasetGroups", () => {
    const saga = dataset.effects.getDatasetGroups
    const creator = {
      type: "getDatasetGroups",
      payload: {},
    }
    const datetime = '2022-02-14T10:03:49'
    const origin = [1, 2, 3, 4].map(item => {
      return {
        id: item,
        project_id: 1000 + item,
        name: 'name' + item,
        create_datetime: datetime,
      }
    })
    const recieved = origin.map(item => transferDatasetGroup(item))
    const expected = { items: recieved, total: recieved.length }

    const generator = saga(creator, { put, call })
    generator.next()
    const response = generator.next({
      code: 0,
      result: { items: origin, total: origin.length },
    })
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: getDataset", () => {
    const saga = dataset.effects.getDataset
    const creator = {
      type: "getDataset",
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
  it("effects: batchDatasets", () => {
    const saga = dataset.effects.batchDatasets
    const creator = {
      type: "batchDatasets",
      payload: { ids: '1,2' },
    }
    const recieved = [1,3,4].map(id => ds(id))
    const expected = recieved.map(item => transferDataset(item))

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: recieved,
    })

    expect(expected).toEqual(end.value)
    expect(end.done).toBe(true)
  })
  it("effects: getAssetsOfDataset", () => {
    const saga = dataset.effects.getAssetsOfDataset
    const creator = {
      type: "getAssetsOfDataset",
      payload: {},
    }
    const expected = { items: [1, 2, , 3, 4], total: 4 }

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    const end = generator.next()

    equalObject(expected, end.value)
    expect(end.done).toBe(true)
  })
  it("effects: getAsset", () => {
    const saga = dataset.effects.getAsset
    const creator = {
      type: "getAsset",
      payload: { hash: 'identify_hash_string' },
    }
    const expected = {
      hash: 'identify_hash_string', width: 800, height: 600,
      "size": 0,
      "channel": 3,
      "timestamp": "2021-09-28T08:26:53.088Z",
      "url": "string",
      "annotations": [
        {}
      ],
      "metadata": {},
      "keywords": [
        "string"
      ]
    }

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    const end = generator.next()

    equalObject(expected, end.value)
    expect(end.done).toBe(true)
  })
  it("effects: delDataset", () => {
    const saga = dataset.effects.delDataset
    const creator = {
      type: "delDataset",
      payload: { id: 10001 },
    }
    const expected = { id: 10001, name: 'del_dataset_name' }

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    equalObject(expected, end.value)
    expect(end.done).toBe(true)
  })
  it("effects: createDataset", () => {
    const saga = dataset.effects.createDataset
    const expected = { id: 10001, name: 'new_dataset_name' }
    const creator = {
      type: "createDataset",
      payload: { id: 10001, name: 'new_dataset_name', type: 1 },
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
  it("effects: updateDataset", () => {
    const saga = dataset.effects.updateDataset
    const creator = {
      type: "updateDataset",
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
  it("effects: updateDatasets -> normal success", () => {
    const saga = dataset.effects.updateDatasets
    const ds = (id, state, progress) => ({ id, hash: `hash${id}`, state, progress })
    const versions = {
      '34': [ds(1, 2, 0.20), ds(2, 3, 1), ds(3, 3, 1)],
      '35': [ds(4, 3, 1), ds(5, 3, 1), ds(6, 3, 1)],
      '36': [ds(7, 2, 0.96), ds(8, 3, 1)],
    }
    const creator = {
      type: "updateDatasets",
      payload: { hash1: { id: 1, state: 2, percent: 0.45 }, hash7: { id: 7, state: 3, percent: 1 } },
    }
    const expected = {
      '34': [ds(1, 2, 0.45), ds(2, 3, 1), ds(3, 3, 1)],
      '35': [ds(4, 3, 1), ds(5, 3, 1), ds(6, 3, 1)],
      '36': [ds(7, 3, 1), ds(8, 3, 1)],
    }

    const generator = saga(creator, { put, call, select })
    generator.next()
    const d = generator.next(versions)
    const end = generator.next()
    const updated = d.value.payload.action.payload

    expect(updated).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: updateDatasets -> empty success", () => {
    const saga = dataset.effects.updateDatasets
    const versions = {
      '34': [ds(1, 2, 0.20), ds(2, 3, 1), ds(3, 3, 1)],
      '35': [ds(4, 3, 1), ds(5, 3, 1), ds(6, 3, 1)],
      '36': [ds(7, 2, 0.96), ds(8, 3, 1)],
    }
    const creator = {
      type: "updateDatasets",
    }

    const generator = saga(creator, { put, call, select })
    generator.next()
    const d = generator.next(versions)
    const end = generator.next()
    const updated = d.value.payload.action.payload

    expect(updated).toEqual(versions)
    expect(end.done).toBe(true)
  })
  it("effects: getHotDatasets -> get stats result success-> batch datasets success", () => {
    const saga = dataset.effects.getHotDatasets
    const creator = {
      type: "getHotDatasets",
      payload: { limit: 3 },
    }
    const result = [[1, 34], [1001, 31], [23, 2]]
    const datasets = [{ id: 1 }, { id: 1001 }, { id: 23 }]
    const expected = [{ id: 1, count: 34 }, { id: 1001, count: 31 }, { id: 23, count: 2 }]

    const generator = saga(creator, { put, call, select })
    generator.next()
    generator.next({
      code: 0,
      result,
    })
    const end = generator.next(datasets)

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: getHotDatasets -> get stats result success-> batch datasets failed", () => {
    const saga = dataset.effects.getHotDatasets
    const creator = {
      type: "getHotDatasets",
      payload: { limit: 3 },
    }
    const result = [[1, 34], [1001, 31], [23, 2]]
    const datasets = undefined
    const expected = []

    const generator = saga(creator, { put, call, select })
    generator.next()
    generator.next({
      code: 0,
      result,
    })
    const end = generator.next(datasets)

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: getHotDatasets -> stats result = []", () => {
    const saga = dataset.effects.getHotDatasets
    const creator = {
      type: "getHotDatasets",
      payload: { limit: 4 },
    }
    const result = []
    const expected = []

    const generator = saga(creator, { put, call, select })
    generator.next()
    const end = generator.next({
      code: 0,
      result,
    })

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: getInternalDataset", () => {
    const saga = dataset.effects.getInternalDataset
    const creator = {
      type: "getInternalDataset",
      payload: {},
    }
    const recieved = [1,3,4,5,6].map(id => ds(id))
    const expected = { items: recieved.map(item => transferDataset(item)), total: recieved.length }

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
})
