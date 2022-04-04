import {
  getModels,
  getModelVersions,
  batchModels,
  queryModels,
  getModel,
  delModel,
  delModelGroup,
  importModel,
  updateModel,
  verify,
} from "@/services/model"
import { getStats } from "../services/common"
import { transferModelGroup, transferModel, states, } from '@/constants/model'

const initQuery = {
  name: "",
  time: 0,
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
  state: initState,
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
    *getModel({ payload }, { call, put }) {
      const { code, result } = yield call(getModel, payload)
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
          payload: model,
        })
        return model
      }
    },
    *delModel({ payload }, { call, put }) {
      const { code, result } = yield call(delModel, payload)
      if (code === 0) {
        return result
      }
    },
    *delModelGroup({ payload }, { call, put }) {
      const { code, result } = yield call(delModelGroup, payload)
      if (code === 0) {
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
    *verify({ payload }, { call }) {
      const { id, urls, image, config } = payload
      const { code, result } = yield call(verify, id, urls, image, config)
      if (code === 0) {
        return result
      }
    },
    *updateModelsStates({ payload }, { put }) {
      const versions = yield select(state => state.model.versions)
      const updateList = payload || {}
      Object.keys(versions).forEach(gid => {
        const models = versions[gid]
        const needUpdate = false
        const updatedModels = models.map(model => {
          const updateItem = updateList[model.hash]
          if (updateItem) {
            needUpdate = true
            model.state = updateItem.state
            model.progress = updateItem.percent
          }
          return { ...model }
        })
        if (needUpdate) {
          put({
            type: 'UPDATE_VERSIONS',
            payload: { id: gid, versions: updatedModels },
          })
        }
      })
    },
    *getModelsByRef({ payload }, { call, put }) {
      const { code, result } = yield call(getStats, { ...payload, q: 'hms' })
      let models = []
      if (code === 0) {
        const refs = {}
        const ids = result.map(item => {
          refs[item[0]] = item[1]
          return item[0]
        })
        if (ids.length) {
          const modelsObj = yield put.resolve({ type: 'batchModels', payload: ids })
          if (modelsObj) {
            models = modelsObj.map(model => {
              model.count = refs[model.id]
              return model
            })
          }
        }
      }
      return models
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
              kmodels[kw] = result[kw].map(item => {
                const { id, name, map } = modelsObj.find(model => model.id === item[0])
                if (name) {
                  return {
                    id, map, name,
                  }
                }
              })
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
        versions: vs,
      }
    },
    UPDATE_ALL_MODELS(state, { payload }) {
      return {
        ...state,
        allModels: payload
      }
    },
    UPDATE_MODEL(state, { payload }) {
      return {
        ...state,
        model: payload
      }
    },
    UPDATE_QUERY(state, { payload }) {
      return {
        ...state,
        query: payload,
      }
    },
    CLEAR_ALL() {
      return { ...initState }
    },
  },
}
