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
  updateModel,
  verify,
  setRecommendStage,
  batchModelStages,
} from "@/services/model"
import { getStats } from "../services/common"
import { transferModelGroup, transferModel, getModelStateFromTask, states, transferStage, } from '@/constants/model'
import { transferAnnotation } from '@/constants/dataset'
import { actions, updateResultState } from '@/constants/common'
import { deepClone } from '@/utils/object'

const initQuery = {
  name: "",
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

export default {
  namespace: "model",
  state: deepClone(initState),
  effects: {
    *getModelGroups({ payload }, { call, put }) {
      const { pid, query } = payload
      const { code, result } = yield call(getModels, pid, query)
      if (code === 0) {
        const groups = result.items.map(item => transferModelGroup(item))
        const models = { items: groups, total: result.total }
        yield put({
          type: "UPDATE_MODELS",
          payload: models,
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
        const ms = result.items.map(model => transferModel(model))
        const vs = { id: gid, versions: ms }
        yield put({
          type: "UPDATE_VERSIONS",
          payload: vs,
        })
        return ms
      }
    },
    *queryModels({ payload }, { select, call, put }) {
      const { code, result } = yield call(queryModels, payload)
      if (code === 0) {
        return { items: result.items.map(ds => transferModel(ds)), total: result.total }
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
      const dss = yield put.resolve({ type: 'queryModels', payload: { project_id: pid, state: states.VALID, limit: 10000 } })
      if (dss) {
        yield put({
          type: "UPDATE_ALL_MODELS",
          payload: dss.items,
        })
        return dss.items
      }
    },
    *batchModels({ payload }, { call, put }) {
      const { code, result } = yield call(batchModels, payload)
      if (code === 0) {
        const models = result.map(model => transferModel(model))
        return models
      }
    },
    *getModel({ payload }, { call, put, select }) {
      const { id, force } = payload
      if (!force) {
        const modelCache = yield select(state => state.model.model[id])
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
          type: "UPDATE_MODEL",
          payload: { id, model },
        })
        return model
      }
    },
    *delModel({ payload }, { call, put }) {
      const { code, result } = yield call(delModel, payload)
      if (code === 0) {
        yield put({
          type: 'UPDATE_MODEL',
          payload: { id: payload, model: {} },
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
        return result
      }
    },
    *restore({ payload: { pid, ids = [] } }, { call, put }) {
      const { code, result } = yield call(batchAct, actions.restore, pid, ids)
      if (code === 0) {
        yield put.resolve({ type: 'clearCache' })
        return result
      }
    },
    *importModel({ payload }, { call, put }) {
      const { code, result } = yield call(importModel, payload)
      if (code === 0) {
        return result
      }
    },
    *updateModel({ payload }, { call, put }) {
      const { id, name } = payload
      const { code, result } = yield call(updateModel, id, name)
      if (code === 0) {
        return result
      }
    },
    *setRecommendStage({ payload }, { call, put }) {
      const { model, stage } = payload
      const { code, result } = yield call(setRecommendStage, model, stage)
      if (code === 0) {
        return transferModel(result)
      }
    },
    *verify({ payload }, { call }) {
      const { code, result } = yield call(verify, payload)
      if (code === 0) {
        return result.annotations[0]?.detection?.map(transferAnnotation)
      }
    },
    *batchModelStages({ payload }, { call, put }) {
      const { code, result } = yield call(batchModelStages, payload)
      if (code === 0) {
        const stages = result.map(stage => transferStage(stage))
        return stages || []
      }
    },
    *updateModelsStates({ payload }, { put, select }) {
      const versions = yield select(state => state.model.versions)
      const tasks = payload || {}
      const all = yield select(({ model }) => model.allModels)
      const newModels = []
      Object.keys(versions).forEach(gid => {
        const models = versions[gid]
        const updatedModels = models.map(model => {
          const updatedModel = updateResultState(model, tasks)
          newModels.push(updatedModel)
          return updatedModel ? { ...updatedModel } : model
        })
        versions[gid] = updatedModels
      })
      const validNewModels = newModels.filter(model => model?.needReload)
      yield put({
        type: 'UPDATE_ALL_MODELS',
        payload: [...validNewModels, ...all],
      })
      yield put({
        type: 'UPDATE_ALL_VERSIONS',
        payload: { ...versions },
      })
    },
    *updateModelState({ payload }, { put, select }) {
      const models = yield select(state => state.model.model)
      const tasks = payload || {}
      const id = Object.keys(models).find(id => models[id])
      const updatedModel = updateResultState(models[id], tasks)

      if (updatedModel) {
        yield put({
          type: 'UPDATE_MODEL',
          payload: { id: updatedModel.id, model: { ...updatedModel } },
        })
      }
    },
    *getModelsByMap({ payload }, { call, put }) {
      const { code, result } = yield call(getStats, { ...payload, q: 'mms' })
      let kws = []
      let kmodels = {}
      if (code === 0) {
        kws = Object.keys(result).slice(0, 5)
        const ids = [...new Set(kws.reduce((prev, current) => ([...prev, ...result[current].map(item => item[0])]), []))]
        if (ids.length) {
          const modelsObj = yield put.resolve({ type: 'batchModels', payload: ids })
          if (modelsObj) {
            kws.forEach(kw => {
              kmodels[kw] = [...new Set(result[kw].map(item => {
                const model = modelsObj.find(model => model.id === item[0])
                return model ? model : null
              }))]
            })
          }
        }
      }
      return {
        keywords: kws, kmodels,
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
        }
      })
    },
    *resetQuery({ }, { put }) {
      yield put({
        type: 'UPDATE_QUERY',
        payload: initQuery,
      })
    },
    *clearCache({ }, { put }) {
      yield put({ type: 'CLEAR_ALL', })
    },
  },
  reducers: {
    UPDATE_MODELS(state, { payload }) {
      return {
        ...state,
        models: payload
      }
    },
    UPDATE_VERSIONS(state, { payload }) {
      const { id, versions } = payload
      const vs = state.versions
      vs[id] = versions
      return {
        ...state,
        versions: { ...vs },
      }
    },
    UPDATE_ALL_VERSIONS(state, { payload }) {
      return {
        ...state,
        versions: { ...payload },
      }
    },
    UPDATE_ALL_MODELS(state, { payload }) {
      return {
        ...state,
        allModels: payload
      }
    },
    UPDATE_MODEL(state, { payload }) {
      const { id, model } = payload
      const models = { ...state.model, [id]: model }
      return {
        ...state,
        model: { ...models },
      }
    },
    UPDATE_QUERY(state, { payload }) {
      return {
        ...state,
        query: payload,
      }
    },
    CLEAR_ALL() {
      return deepClone(initState)
    },
  },
}
