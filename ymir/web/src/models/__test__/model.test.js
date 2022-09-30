import model from "../model"
import { put, putResolve, select, call } from "redux-saga/effects"
import { errorCode, generatorCreator, product, products, list, response } from './func'
import { transferModelGroup, transferModel, states } from '@/constants/model'
import { transferAnnotation } from '@/constants/dataset'

put.resolve = putResolve

jest.mock('umi', () => {
  return {
    getLocale() {
      return 'en-US'
    }
  }
})

describe("models: model", () => {
  const createGenerator = generatorCreator(model)
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

  const groupsResult = products(7).map(({ id }) => ({ id, create_datetime: createTime }))
  const groupsExpected = groupsResult.map(item => transferModelGroup(item))
  const modelsResult = products(4).map(({ id }) => md(id))
  const modelsExpected = modelsResult.map(item => transferModel(item))

  const generateNormal = ({
    func,
    result,
    expected,
    payload = {},
    label = '',
    hasForce = false,
    force = false,
    cache = null,
  }) => {
    it(`effects: ${func} -> ${label} -> success`, () => {
      const generator = createGenerator(func, payload)
      let end = generator.next()

      if (hasForce) {
        if (!force) {
          end = generator.next(cache || {})
        }

        if (force || !cache) {
          const res = generator.next(result)
          end = generator.next()
        }
      } else {
        end = generator.next(result)
        if (!end.done) {
          end = generator.next()
        }
      }

      expect(end.value).toEqual(expected)
      expect(end.done).toBe(true)
    })
  }

  const generateList = (func, payload, result, expected) => generateNormal({
    func, payload, result, expected
  })

  const generateForce = ({ func, result, expected, payload, label, force, cache }) => generateNormal({
    func, payload: { ...payload, force }, force, result, expected, label, cache, hasForce: true,
  })

  const generateGetModelVersions = (label, result, expected, force = false, hasCache = false) => {
    const gid = 2325234
    const cache = hasCache ? { [gid]: expected } : null
    return generateForce({
      label, force, cache, result, expected,
      func: 'getModelVersions', payload: { gid },
    })
  }

  it("reducers: UPDATE_MODELS, UPDATE_MODEL", () => {
    const state = {
      models: {},
      model: {},
    }
    const expected = products(10)
    const action = {
      payload: list(expected),
    }
    const { models } = model.reducers.UPDATE_MODELS(state, action)
    const { items, total } = models
    expect(items).toEqual(expected)
    expect(total).toBe(expected.length)

    const expectedId = 1001
    const daction = {
      payload: { id: expectedId, model: { id: expectedId } }
    }
    const result = model.reducers.UPDATE_MODEL(
      state,
      daction
    )
    expect(result.model[expectedId].id).toBe(expectedId)
  })

  errorCode(model, 'getModelGroups')
  errorCode(model, 'batchModels')
  errorCode(model, 'getModel', { id: 342134, force: true })
  errorCode(model, 'delModel')
  errorCode(model, 'importModel')
  errorCode(model, 'updateModel')
  errorCode(model, 'setRecommendStage')
  errorCode(model, 'verify')
  errorCode(model, 'getModelsByMap', 10025, { keywords: [], kmodels: {} })
  errorCode(model, 'getModelVersions', { id: 235234, force: true })
  errorCode(model, 'queryModels')
  errorCode(model, 'delModelGroup')
  errorCode(model, 'hide')
  errorCode(model, 'restore')

  // todo list
  // updateModelsStates
  // updateModelState
  // updateQuery
  // resetQuery
  // clearCache

  generateList('getModelGroups', {}, response(list(groupsResult)), list(groupsExpected))

  // getModelVersion
  generateGetModelVersions('force = false && cache = false', response(list(modelsResult)), modelsExpected)
  generateGetModelVersions('force = true', response(list(modelsResult)), modelsExpected, true)
  generateGetModelVersions('force = false && cache = true', response(list(modelsResult)), modelsExpected, false, true)

  // queryModels
  generateList('queryModels', {}, response(list(modelsResult)), list(modelsExpected))
  generateList('getHiddenList', {}, list(modelsExpected), list(modelsExpected))
  generateList('queryAllModels', 63453, list(modelsExpected), modelsExpected)
  generateList('batchModels', { ids: '1,3' }, response(modelsResult), modelsExpected)
  generateList('hide', {pid: 324334, ids: [53, 34]}, response(list(modelsExpected)), list(modelsExpected))
  generateList('restore', {pid: 324334, ids: [63, 23]}, response(list(modelsExpected)), list(modelsExpected))


  generateNormal({
    func: 'delModelGroup',
    payload: { id: 4235234234 },
    result: response('ok'),
    expected: 'ok',
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

    const generator = saga(creator, { put, call, select })
    generator.next()
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
    generator.next({
      code: 0,
      result: expected,
    })
    const end = generator.next()

    expect(end.value.id).toBe(expected.id)
    expect(end.done).toBe(true)
  })
  it("effects: importModel", () => {
    const saga = model.effects.importModel
    const expected = { id: 618, name: 'anewmodel' }
    const creator = {
      type: "importModel",
      payload: { projectId: 6181, name: expected.name, url: '/testmodellocalurl' },
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
  it("effects: setRecommendStage", () => {
    const saga = model.effects.setRecommendStage
    const modelId = 13412
    const stage = 23234
    const params = { modelId, stage, }
    const expected = md(modelId)
    const creator = {
      type: "setRecommendStage",
      payload: params,
    }

    const generator = saga(creator, { put, call })
    const start = generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    expect(end.value).toEqual(transferModel(expected))
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
    const boxes = [{ box: { x: 20, y: 52, w: 79, h: 102 }, keyword: 'cat', score: 0.8 }]
    const expected = {
      model_id: id,
      annotations: [
        { img_url: url, detection: boxes }
      ]
    }

    const generator = saga(creator, { put, call })
    const start = generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    expect(end.value).toEqual(boxes.map(transferAnnotation))
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
      result[keyword] = models.map(model => [model.id, model.map])
    })
    keywords.slice(0, 5).forEach((keyword, index) => {
      kmodels[keyword] = models
    })
    const expected = { kmodels, keywords: keywords.slice(0, 5) }

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
      result[keyword] = models.map(model => [model.id, model.map])
    })

    const generator = saga(creator, { put, call, select })
    generator.next()
    generator.next({
      code: 0,
      result,
    })
    const end = generator.next(undefined)

    expect(end.value).toEqual({ keywords: keywords.slice(0, 5), kmodels: {} })
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

    expect(end.value).toEqual({ keywords: [], kmodels: {} })
    expect(end.done).toBe(true)
  })
})
