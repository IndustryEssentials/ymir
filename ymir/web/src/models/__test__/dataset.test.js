import dataset from "../dataset"
import { put, call } from "redux-saga/effects"

function equalObject(obj1, obj2) {
  expect(JSON.stringify(obj1)).toBe(JSON.stringify(obj2))
}

describe("models: dataset", () => {
  it("reducers: UPDATE_DATASETS", () => {
    const state = {
      datasets: {},
    }
    const expected = {items: [1,2,3,4], total: 4}
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
    expect(result.dataset.id).toBe(expected.id)
  })
  it("reducers: UPDATE_ASSETS", () => {
    const state = {
      assets: {},
    }
    const expected = {items: [1,2,3,4], total: 4}
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
    const expected = {hash: 'test'}
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
    const expected = [1,2,3,4]
    const action = {
      payload: expected,
    }
    const result = dataset.reducers.UPDATE_PUBLICDATASETS(state, action)
    expect(result.publicDatasets.join(',')).toBe(expected.join(','))
  })

  it("effects: getDatasets", () => {
    const saga = dataset.effects.getDatasets
    const creator = {
      type: "getDatasets",
      payload: {},
    }
    const expected = { items: [1, 2, , 3, 4], total: 4 }

    const generator = saga(creator, { put, call })
    generator.next()
    const response = generator.next({
      code: 0,
      result: expected,
    })
    const end = generator.next()

    // console.log('dataset model - getDatasets:', response, end, typeof end.value)
    equalObject(expected, end.value)
    expect(end.done).toBe(true)
  })
  it("effects: getDataset", () => {
    const saga = dataset.effects.getDataset
    const creator = {
      type: "getDataset",
      payload: {},
    }
    const expected = { id: 1001, name: 'dataset001' }

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
  it("effects: batchDatasets", () => {
    const saga = dataset.effects.batchDatasets
    const creator = {
      type: "batchDatasets",
      payload: { ids: '1,2,3' },
    }
    const expected = { items: [1, 2, , 3, 4], total: 4 }

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    equalObject(expected.items, end.value)
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
      payload: {id: 10001},
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
    const expected = {id: 10001, name: 'new_dataset_name'}
    const creator = {
      type: "createDataset",
      payload: {id: 10001, name: 'new_dataset_name', type: 1 },
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
      payload: {id: 10001, name: 'new_dataset_name'},
    }
    const expected = {id: 10001, name: 'new_dataset_name'}

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    equalObject(expected, end.value)
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
  it("effects: importDataset", () => {
    const saga = dataset.effects.importDataset
    const creator = {
      type: "importDataset",
      payload: {},
    }
    const expected = { id: 1001, name: 'import_dataset_name' }

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
