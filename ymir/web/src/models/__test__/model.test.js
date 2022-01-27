import model from "../model"
import { put, putResolve, select, call } from "redux-saga/effects"
import { errorCode } from './func'

put.resolve = putResolve

describe("models: model", () => {
  const product = (id) => ({ id })
  const products = (n) => Array.from({ length: n }, (item, index) => product(index + 1))

  it("reducers: UPDATE_MODELS, UPDATE_MODEL", () => {
    const state = {
      models: {},
      model: {},
    }
    const expected = products(10)
    const action = {
      payload: { items: expected, total: expected.length },
    }
    const { models } = model.reducers.UPDATE_MODELS(state, action)
    const { items, total } = models
    expect(items.join(',')).toBe(expected.join(','))
    expect(total).toBe(expected.length)

    const expectedId = 1001
    const daction = {
      payload: { id: expectedId }
    }
    const result = model.reducers.UPDATE_MODEL(
      state,
      daction
    )
    expect(result.model.id).toBe(expectedId)
  })

  errorCode(model, 'getModels')
  errorCode(model, 'batchModels')
  errorCode(model, 'getModel')
  errorCode(model, 'delModel')
  errorCode(model, 'createModel')
  errorCode(model, 'updateModel')
  errorCode(model, 'verify')
  errorCode(model, 'getModelsByRef', [])
  errorCode(model, 'getModelsByMap', {keywords: [], kmodels: {}})

  it("effects: getModels", () => {
    const saga = model.effects.getModels
    const creator = {
      type: "getModels",
      payload: {},
    }
    const expected = products(8)

    const generator = saga(creator, { put, call })
    const start = generator.next()
    generator.next({
      code: 0,
      result: { items: expected, total: expected.length },
    })
    const end = generator.next()

    expect(end.value.items.join('')).toBe(expected.join(''))
    expect(end.done).toBe(true)
  })
  it("effects: batchModels", () => {
    const saga = model.effects.batchModels
    const creator = {
      type: "batchModels",
      payload: { ids: '1,3' },
    }
    const expected = products(2)

    const generator = saga(creator, { put, call })
    const start = generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    expect(end.value.join('')).toBe(expected.join(''))
    expect(end.done).toBe(true)
  })
  it("effects: getModel", () => {
    const saga = model.effects.getModel
    const modelId = 615
    const datasetId = 809
    const vsId = 810
    const creator = {
      type: "getModel",
      payload: { id: modelId },
    }

    const expected = {
      id: modelId,
      parameters: {
        include_train_datasets: [datasetId],
        include_validation_datasets: [vsId],
      }
    }
    const datasets = [product(datasetId), product(vsId), product(0), product(1)]

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    generator.next(datasets)
    const end = generator.next()
    const { id, parameters, trainSets } = end.value
    expect(id).toBe(modelId)
    expect(parameters.include_train_datasets[0]).toBe(datasetId)
    expect(trainSets[0].id).toBe(datasetId)
    expect(end.done).toBe(true)
  })
  it("effects: delModel", () => {
    const saga = model.effects.delModel
    const creator = {
      type: "delModel",
      payload: { id: 616 },
    }
    const expected = { id: 617 }

    const generator = saga(creator, { put, call })
    const start = generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    expect(end.value.id).toBe(expected.id)
    expect(end.done).toBe(true)
  })
  it("effects: createModel", () => {
    const saga = model.effects.createModel
    const expected = { id: 618, name: 'anewmodel' }
    const creator = {
      type: "createModel",
      payload: expected,
    }

    const generator = saga(creator, { put, call })
    const start = generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    expect(end.value.id).toBe(expected.id)
    expect(end.done).toBe(true)
  })
  it("effects: updateModel", () => {
    const saga = model.effects.updateModel
    const expected = { id: 619 }
    const creator = {
      type: "updateModel",
      payload: { ...expected, name: 'itisanewname' },
    }

    const generator = saga(creator, { put, call })
    const start = generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    expect(end.value.id).toBe(expected.id)
    expect(end.done).toBe(true)
  })
  it("effects: verify", () => {
    const saga = model.effects.verify
    const id = 620
    const url = '/test.jpg'
    const creator = {
      type: "verify",
      payload: { id, urls: [url] },
    }
    const expected = {
      model_id: id,
      annotations: [
        { img_url: url, detections: [{ box: { x: 20, y: 52, w: 79, h: 102 } }] }
      ]
    }

    const generator = saga(creator, { put, call })
    const start = generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    expect(end.value.model_id).toBe(id)
    expect(end.done).toBe(true)
  })

//   getModelsByRef
it("effects: getModelsByRef -> get stats result success-> batch models success", () => {
  const saga = model.effects.getModelsByRef
  const creator = {
    type: "getModelsByRef",
    payload: { limit: 3 },
  }
  const models = products(12)
  const result = models.map((model, index) => [model.id, index])
  const expected = models.map((model, index) => ({ id: model.id, count: index }))

  const generator = saga(creator, { put, call, select })
  generator.next()
  generator.next({
    code: 0,
    result,
  })
  const end = generator.next(models)

  expect(end.value).toEqual(expected)
  expect(end.done).toBe(true)
})
it("effects: getModelsByRef -> get stats result success-> batch models success", () => {
  const saga = model.effects.getModelsByRef
  const creator = {
    type: "getModelsByRef",
    payload: { limit: 3 },
  }
  const models = products(12)
  const result = models.map((model, index) => [model.id, index])
  const expected = models.map((model, index) => ({ id: model.id, count: index }))

  const generator = saga(creator, { put, call, select })
  generator.next()
  generator.next({
    code: 0,
    result,
  })
  const end = generator.next(models)

  expect(end.value).toEqual(expected)
  expect(end.done).toBe(true)
})
it("effects: getModelsByRef -> get stats result success-> batch models failed", () => {
  const saga = model.effects.getModelsByRef
  const creator = {
    type: "getModelsByRef",
    payload: { limit: 3 },
  }
  const models = products(12)
  const result = models.map((model, index) => [model.id, index])
  const expected = models.map((model, index) => ({ id: model.id, count: index }))

  const generator = saga(creator, { put, call, select })
  generator.next()
  generator.next({
    code: 0,
    result,
  })
  const end = generator.next(undefined)

  expect(end.value).toEqual([])
  expect(end.done).toBe(true)
})
it("effects: getModelsByRef -> get stats result = []", () => {
  const saga = model.effects.getModelsByRef
  const creator = {
    type: "getModelsByRef",
    payload: { limit: 3 },
  }
  const result = []

  const generator = saga(creator, { put, call, select })
  generator.next()
  const end = generator.next({
    code: 0,
    result,
  })

  expect(end.value).toEqual([])
  expect(end.done).toBe(true)
})
// getModelsByMap
it("effects: getModelsByMap -> get stats result success-> batch models success", () => {
  const saga = model.effects.getModelsByMap
  const creator = {
    type: "getModelsByMap",
    payload: { limit: 30 },
  }
  const keywords = ['cat', 'dog', 'person', 'tree', 'cup', 'light', 'phone']
  const models = products(5).map(({ id }) => ({ id, name: `model${id}`, map: 0.1 * (id + 1) }))
  const result = {}
  const kmodels = {}
  keywords.forEach((keyword, index) => {
    result[keyword] = models.map(model => [ model.id, model.map ])
  })
  keywords.slice(0, 5).forEach((keyword, index) => {
    kmodels[keyword] = models
  })
  const expected = { kmodels, keywords: keywords.slice(0, 5)}

  const generator = saga(creator, { put, call, select })
  generator.next()
  generator.next({
    code: 0,
    result,
  })
  const end = generator.next(models)

  expect(end.value).toEqual(expected)
  expect(end.done).toBe(true)
})
it("effects: getModelsByMap -> get stats result success-> batch models failed", () => {
  const saga = model.effects.getModelsByMap
  const creator = {
    type: "getModelsByMap",
    payload: { limit: 30 },
  }
  const keywords = ['cat', 'dog', 'person', 'tree', 'cup', 'light', 'phone']
  const models = products(5).map(({ id }) => ({ id, name: `model${id}`, map: 0.1 * (id + 1) }))
  const result = {}
  keywords.forEach((keyword, index) => {
    result[keyword] = models.map(model => [ model.id, model.map ])
  })

  const generator = saga(creator, { put, call, select })
  generator.next()
  generator.next({
    code: 0,
    result,
  })
  const end = generator.next(undefined)

  expect(end.value).toEqual({keywords: keywords.slice(0, 5), kmodels: {}})
  expect(end.done).toBe(true)
})
it("effects: getModelsByMap -> get stats result = []", () => {
  const saga = model.effects.getModelsByMap
  const creator = {
    type: "getModelsByMap",
    payload: { limit: 30 },
  }
  const result = {}

  const generator = saga(creator, { put, call, select })
  generator.next()
  const end = generator.next({
    code: 0,
    result,
  })

  expect(end.value).toEqual({keywords: [], kmodels: {}})
  expect(end.done).toBe(true)
})
})
