import model from "../model"
import { put, putResolve, call } from "redux-saga/effects"

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
})
