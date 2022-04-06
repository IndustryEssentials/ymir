import model from "../model"
import { put, putResolve, select, call } from "redux-saga/effects"
import { errorCode } from './func'
import { transferModelGroup, transferModel, states } from '@/constants/model'

put.resolve = putResolve

jest.mock('umi', () => {
  return {
    getLocale() {
      return 'en-US'
    }
  }
})

describe("models: model", () => {
  const product = (id) => ({ id })
  const products = (n) => Array.from({ length: n }, (item, index) => product(index + 1))
  
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
  const md = id => ({
    id,
    hash: 'testhash',
    map: 0.88,
    state: 2,
    version_num: 2,
    "create_datetime": createTime,
    "update_datetime": createTime,
    related_task: task,
  })

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

  errorCode(model, 'getModelGroups')
  errorCode(model, 'batchModels')
  errorCode(model, 'getModel')
  errorCode(model, 'delModel')
  errorCode(model, 'importModel')
  errorCode(model, 'updateModel')
  errorCode(model, 'verify')
  errorCode(model, 'getModelsByRef', [])
  errorCode(model, 'getModelsByMap', {keywords: [], kmodels: {}})

  it("effects: getModelGroups", () => {
    const saga = model.effects.getModelGroups
    const creator = {
      type: "getModelGroups",
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
    const recieved = products(2).map(id => md(id))
    const expected = recieved.map(item => transferModel(item))

    const generator = saga(creator, { put, call })
    const start = generator.next()
    const end = generator.next({
      code: 0,
      result: recieved,
    })

    expect(end.value).toEqual(expected)
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

    const recieved = md(modelId)
    const expected = transferModel(recieved)

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: recieved,
    })
    const end = generator.next()
    expect(end.value).toEqual(expected)
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
  it("effects: importModel", () => {
    const saga = model.effects.importModel
    const expected = { id: 618, name: 'anewmodel' }
    const creator = {
      type: "importModel",
      payload: { projectId: 6181, name: expected.name, url: '/testmodellocalurl'},
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
