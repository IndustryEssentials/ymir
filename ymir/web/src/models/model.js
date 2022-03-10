import {
  getModels,
  getModelVersions,
  batchModels,
  getModel,
  delModel,
  createModel,
  updateModel,
  verify,
} from "@/services/model"
import { getStats } from "../services/common"
import { transferModelGroup, transferModelVersion } from '@/constants/model'

const initQuery = {
  name: "",
  time: 0,
  offset: 0,
  limit: 20,
}

export default {
  namespace: "model",
  state: {
    query: initQuery,
    models: {
      items: [],
      total: 0,
    },
    versions: {},
    model: {},
  },
  effects: {
    *getModels({ payload }, { call, put }) {
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
        const ms = result.models.map(model => transferModelVersion(model))
        const vs = { id: gid, versions: ms }
        yield put({
          type: "UPDATE_VERSIONS",
          payload: vs,
        })
        return ms
      }
    },
    *batchModels({ payload }, { call, put }) {
      const { code, result } = yield call(batchModels, payload)
      if (code === 0) {
        return result
      }
    },
    *getModel({ payload }, { call, put }) {
      const { code, result } = yield call(getModel, payload)
      if (code === 0) {
        const pa = result.parameters || {}
        const trainSets = pa?.include_train_datasets || []
        const testSets = pa?.include_validation_datasets || []
        const ids = [
          ...trainSets,
          ...testSets,
        ]
        if (ids.length) {
          const datasets = yield put.resolve({ type: 'dataset/batchDatasets', payload: ids })
          if (datasets && datasets.length) {
            result['trainSets'] = trainSets.map(sid => datasets.find(ds => ds.id === sid))
            result['testSets'] = testSets.map(sid => datasets.find(ds => ds.id === sid))
          }
        }
        yield put({
          type: "UPDATE_MODEL",
          payload: result,
        })
        return result
      }
    },
    *delModel({ payload }, { call, put }) {
      const { code, result } = yield call(delModel, payload)
      if (code === 0) {
        return result
      }
    },
    *createModel({ payload }, { call, put }) {
      const { code, result } = yield call(createModel, payload)
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
      const { id, urls, image } = payload
      const { code, result } = yield call(verify, id, urls, image)
      if (code === 0) {
        return result
      }
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
  },
}
