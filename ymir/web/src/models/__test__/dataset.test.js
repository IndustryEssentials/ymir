import dataset from "../dataset"
import { put, putResolve, call, select } from "redux-saga/effects"
import { errorCode } from './func'
import { format } from '@/utils/date'

put.resolve = putResolve

function equalObject(obj1, obj2) {
  expect(JSON.stringify(obj1)).toBe(JSON.stringify(obj2))
}

describe("models: dataset", () => {
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
    const resp = [1, 2, 3, 4].map(item => ({
      id: item,
      projectId: 1000 + item,
      name: 'name' + item,
      createTime: format(datetime),
    }))
    const expected = { items: origin, total: origin.length }

    const generator = saga(creator, { put, call })
    generator.next()
    const response = generator.next({
      code: 0,
      result: expected,
    })
    const end = generator.next()

    equalObject({ items: resp, total: resp.length }, end.value)
    expect(end.done).toBe(true)
  })
  it("effects: getDataset", () => {
    const saga = dataset.effects.getDataset
    const creator = {
      type: "getDataset",
      payload: { gid: 10002 },
    }
    const createTime = "2022-03-10T03:39:09"
    const send = {
      "name": "p0001_training_dataset",
      "result_state": 1,
      "dataset_group_id": 1,
      // "project_id": 1,
      state: 1,
      "keywords": [],
      "ignored_keywords": [],
      "asset_count": null,
      "keyword_count": null,
      "is_deleted": false,
      "create_datetime": createTime,
      "update_datetime": createTime,
      "id": 1,
      "hash": "t00000020000012afef21646883528",
      "version_num": 0,
      "task_id": 1,
      "user_id": 2,
      "related_task": {
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
    }

    const expected = {
      "id": 1,
      "groupId": 1,
      "projectId": undefined,
      "name": "p0001_training_dataset",
      "version": 0,
      "versionName": "V0",
      "assetCount": 0,
      "keywords": [],
      "keywordCount": 0,
      "ignoredKeywords": [],
      state: 1,
      "hash": "t00000020000012afef21646883528",
      "createTime": format(createTime),
      "updateTime": format(createTime),
      "taskId": 1,
      "progress": 1,
      "taskState": 3,
      "taskType": 105,
      "duration": null,
      "taskName": "t00000020000013277a01646883549"
    }

    const generator = saga(creator, { put, call })
    generator.next()
    const calls = generator.next({
      code: 0,
      result: send,
    })
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: batchDatasets", () => {
    const saga = dataset.effects.batchDatasets
    const creator = {
      type: "batchDatasets",
      payload: { ids: '1,2,3,4' },
    }
    const expected = [1, 2, 3, 4]

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    equalObject(expected, end.value)
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
    const datasets = {
      items: [
        { id: 34, hash: 'hash1', state: 2, progress: 20 },
        { id: 35, hash: 'hash2', state: 3, progress: 100 },
        { id: 36, hash: 'hash3', state: 2, progress: 96 },
      ], total: 3
    }
    const creator = {
      type: "updateDatasets",
      payload: { hash1: { id: 34, state: 2, percent: 0.45 }, hash3: { id: 36, state: 3, percent: 1 } },
    }
    const expected = [
      { id: 34, hash: 'hash1', state: 2, progress: 45 },
      { id: 35, hash: 'hash2', state: 3, progress: 100 },
      { id: 36, hash: 'hash3', state: 3, progress: 100, forceUpdate: true },
    ]

    const generator = saga(creator, { put, call, select })
    generator.next()
    const d = generator.next(datasets)
    const end = generator.next()
    const updated = d.value.payload.action.payload.items

    expect(updated).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: updateDatasets -> empty success", () => {
    const saga = dataset.effects.updateDatasets
    const datasets = {
      items: [
        { id: 34, hash: 'hash1', state: 2, progress: 20 },
        { id: 35, hash: 'hash2', state: 3, progress: 100 },
        { id: 36, hash: 'hash3', state: 2, progress: 96 },
      ], total: 3
    }
    const creator = {
      type: "updateDatasets",
    }

    const generator = saga(creator, { put, call, select })
    generator.next()
    const d = generator.next(datasets)
    const end = generator.next()
    const updated = d.value.payload.action.payload

    expect(updated).toEqual(datasets)
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
})
