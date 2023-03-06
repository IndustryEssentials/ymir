import {
  getModels,
  getModelVersions,
  batchModels,
  queryModels,
  getModel,
  delModel,
  delModelGroup,
  batchAct,
  importModel,
  updateModelGroup,
  verify,
  setRecommendStage,
  batchModelStages,
  updateVersion,
} from '@/services/model'
import { getStats } from '../services/common'
import { transferModelGroup, transferModel, transferStage } from '@/constants/model'
import { ResultStates as states } from '@/constants/common'
import { toAnnotation } from '@/constants/asset'
import { actions, updateResultState, updateResultByTask } from '@/constants/common'
import { deepClone } from '@/utils/object'
import { NormalReducer } from './_utils'

const initQuery = {
  name: '',
  time: 0,
  current: 1,
  offset: 0,
  limit: 20,
}

const initState = {
  query: initQuery,
  models: {
    items: [],
    total: 0,
  },
  versions: {},
  model: {},
  allModels: [],
}

const reducers = {
  UPDATE_MODELS: NormalReducer('models'),
  UPDATE_VERSIONS: NormalReducer('versions'),
  UPDATE_ALL_MODELS: NormalReducer('allModels'),
  UPDATE_MODEL: NormalReducer('model'),
  UPDATE_QUERY: NormalReducer('query'),
}

export default {
  namespace: 'model',
  state: deepClone(initState),
  effects: {
    *getModelGroups({ payload }, { call, put }) {
      const { pid, query } = payload
      const { code, result } = yield call(getModels, pid, query)
      if (code === 0) {
        const groups = result.items.map((item) => transferModelGroup(item))
        const models = { items: groups, total: result.total }
        yield put({
          type: 'UPDATE_MODELS',
          payload: { [pid]: models },
        })
        return models
      }
    },
    *getModelVersions({ payload }, { select, call, put }) {
      const { gid, force } = payload
      if (!force) {
        const versions = yield select(({ model }) => model.versions)
        if (versions[gid]) {
          return versions[gid]
        }
      }
      const { code, result } = yield call(getModelVersions, gid)
      if (code === 0) {
        const ms = result.items.map((model) => transferModel(model))
        yield put({
          type: 'UPDATE_VERSIONS',
          payload: { [gid]: ms },
        })
        return ms
      }
    },
    *queryModels({ payload }, { select, call, put }) {
      const { code, result } = yield call(queryModels, payload)
      if (code === 0) {
        return { items: result.items.map((ds) => transferModel(ds)), total: result.total }
      }
    },
    *getHiddenList({ payload }, { put }) {
      const query = { ...{ order_by: 'update_datetime' }, ...payload, visible: false }
      return yield put({
        type: 'queryModels',
        payload: query,
      })
    },
    *queryAllModels({ payload }, { select, call, put }) {
      const pid = payload
      const dss = yield put.resolve({ type: 'queryModels', payload: { pid, state: states.VALID, limit: 10000 } })
      if (dss) {
        yield put({
          type: 'UPDATE_ALL_MODELS',
          payload: dss.items,
        })
        return dss.items
      }
    },
    *batchLocalModels({ payload: ids = [] }, { call, put }) {
      const cache = yield put.resolve({
        type: 'getLocalModels',
        payload: ids,
      })
      if (ids.length === cache.length) {
        return cache
      }
      const fetchIds = ids.filter((id) => cache.every((ds) => ds.id !== id))
      const remoteModels = yield put.resolve({
        type: 'batchModels',
        payload: fetchIds,
      })
      return [...cache, ...remoteModels]
    },
    *batchModels({ payload }, { call, put }) {
      const { code, result } = yield call(batchModels, payload)
      if (code === 0) {
        const models = result.map((model) => transferModel(model))
        yield put({
          type: 'updateLocalModels',
          payload: models,
        })
        return models
      }
    },
    *getModel({ payload }, { call, put, select }) {
      const { id, force } = payload
      if (!force) {
        const modelCache = yield select((state) => state.model.model[id])
        if (modelCache) {
          return modelCache
        }
      }
      const { code, result } = yield call(getModel, id)
      if (code === 0) {
        let model = transferModel(result)
        if (model.projectId) {
          const presult = yield put.resolve({
            type: 'project/getProject',
            payload: { id: model.projectId },
          })
          if (presult) {
            model.project = presult
          }
        }
        yield put({
          type: 'UPDATE_MODEL',
          payload: { [id]: model },
        })
        return model
      }
    },
    *delModel({ payload: id }, { call, put }) {
      const { code, result } = yield call(delModel, id)
      if (code === 0) {
        yield put({
          type: 'UPDATE_MODEL',
          payload: { [id]: undefined },
        })
        return result
      }
    },
    *delModelGroup({ payload }, { call, put }) {
      const { code, result } = yield call(delModelGroup, payload)
      if (code === 0) {
        return result
      }
    },
    *hide({ payload: { pid, ids = [] } }, { call, put }) {
      const { code, result } = yield call(batchAct, actions.hide, pid, ids)
      if (code === 0) {
        const models = (result || []).reduce((prev, md) => ({ ...prev, [md.id]: transferModel(md)}), {})
        yield put({
          type: 'UPDATE_MODEL',
          payload: models,
        })
        return Object.values(models)
      }
    },
    *restore({ payload: { pid, ids = [] } }, { call, put }) {
      const { code, result } = yield call(batchAct, actions.restore, pid, ids)
      if (code === 0) {
        const models = (result || []).reduce((prev, md) => ({ ...prev, [md.id]: transferModel(md)}), {})
        yield put({
          type: 'UPDATE_MODEL',
          payload: models,
        })
        return Object.values(models)
      }
    },
    *importModel({ payload }, { call, put }) {
      const { code, result } = yield call(importModel, payload)
      if (code === 0) {
        const model = transferModel(result)
        yield put({
          type: 'UPDATE_MODEL',
          payload: { [model.id]: model },
        })
        return model
      }
    },
    *updateModelGroup({ payload }, { call, put }) {
      const { id, name } = payload
      const { code, result } = yield call(updateModelGroup, id, name)
      if (code === 0) {
        return result
      }
    },
    *updateVersion({ payload }, { call, put }) {
      const { id, description } = payload
      const { code, result } = yield call(updateVersion, id, description)
      if (code === 0) {
        const model = transferModel(result)
        yield put({
          type: 'UPDATE_MODEL',
          payload: { [model.id]: model },
        })
        return model
      }
    },
    *setRecommendStage({ payload }, { call, put }) {
      const { model, stage } = payload
      const { code, result } = yield call(setRecommendStage, model, stage)
      if (code === 0) {
        const updatedModel = transferModel(result)
        yield put({
          type: 'UPDATE_MODEL',
          payload: { [model]: updatedModel },
        })
        return updatedModel
      }
    },
    *verify({ payload }, { call }) {
      const { code, result } = yield call(verify, payload)
      if (code === 0) {
        return result.annotations[0]?.annotations?.map((anno) => toAnnotation(anno, 0, 0, true))
      }
    },
    *batchModelStages({ payload }, { call, put }) {
      const { code, result } = yield call(batchModelStages, payload)
      if (code === 0) {
        const stages = result.map((stage) => transferStage(stage))
        return stages || []
      }
    },
    *updateModelsStates({ payload }, { put, select }) {
      const versions = yield select((state) => state.model.versions)
      const tasks = payload || {}
      const all = yield select(({ model }) => model.allModels)
      const newModels = []
      Object.keys(versions).forEach((gid) => {
        const models = versions[gid]
        const updatedModels = models.map((model) => {
          const updatedModel = updateResultState(model, tasks)
          newModels.push(updatedModel)
          return updatedModel ? { ...updatedModel } : model
        })
        versions[gid] = updatedModels
      })
      const validNewModels = newModels.filter((model) => model?.needReload)
      yield put({
        type: 'UPDATE_ALL_MODELS',
        payload: [...validNewModels, ...all],
      })
      yield put({
        type: 'UPDATE_VERSIONS',
        payload: { ...versions },
      })
    },
    *updateModelState({ payload }, { put, select }) {
      const caches = yield select((state) => state.model.model)
      const tasks = Object.values(payload || {})
      for (let index = 0; index < tasks.length; index++) {
        const task = tasks[index]
        const model = caches[task?.result_model?.id]
        if (!model) {
          continue
        }
        const updated = updateResultByTask(model, task)
        if (updated) {
          if (updated.needReload) {
            yield put({
              type: 'getModel',
              payload: { id: updated.id, force: true },
            })
          } else {
            yield put({
              type: 'UPDATE_MODEL',
              payload: { [updated.id]: { ...updated } },
            })
          }
        }
      }
    },
    *getModelsByMap({ payload }, { call, put }) {
      const { code, result } = yield call(getStats, { ...payload, q: 'mms' })
      let kws = []
      let kmodels = {}
      if (code === 0) {
        kws = Object.keys(result).slice(0, 5)
        const ids = [...new Set(kws.reduce((prev, current) => [...prev, ...result[current].map((item) => item[0])], []))]
        if (ids.length) {
          const modelsObj = yield put.resolve({ type: 'batchModels', payload: ids })
          if (modelsObj) {
            kws.forEach((kw) => {
              kmodels[kw] = [
                ...new Set(
                  result[kw].map((item) => {
                    const model = modelsObj.find((model) => model.id === item[0])
                    return model ? model : null
                  }),
                ),
              ]
            })
          }
        }
      }
      return {
        keywords: kws,
        kmodels,
      }
    },
    *updateQuery({ payload = {} }, { put, select }) {
      const query = yield select(({ task }) => task.query)
      yield put({
        type: 'UPDATE_QUERY',
        payload: {
          ...query,
          ...payload,
          offset: query.offset === payload.offset ? initQuery.offset : payload.offset,
        },
      })
    },
    *resetQuery({}, { put }) {
      yield put({
        type: 'UPDATE_QUERY',
        payload: initQuery,
      })
    },
    *clearCache({}, { put }) {
      yield put({ type: 'CLEAR_ALL' })
    },
    *updateLocalModels({ payload: models = [] }, { put }) {
      const mds = models.reduce(
        (prev, model) => ({
          ...prev,
          [model.id]: model,
        }),
        {},
      )
      yield put({
        type: 'UPDATE_MODEL',
        payload: mds,
      })
    },
    *getLocalModels({ payload: ids = [] }, { put, select }) {
      const models = yield select(({ model }) => model.model)
      return ids.map((id) => models[id]).filter((d) => d)
    },
  },
  reducers: {
    ...reducers,
    CLEAR_ALL() {
      return deepClone(initState)
    },
  },
}
