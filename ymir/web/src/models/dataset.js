import {
  getDatasetGroups, getDatasetByGroup, queryDatasets, getDataset, batchDatasets, evaluate,
  getAssetsOfDataset, getAsset, batchAct, delDataset, delDatasetGroup, createDataset, updateDataset, getInternalDataset,
} from "@/services/dataset"
import { getStats } from "../services/common"
import { transferDatasetGroup, transferDataset, states } from '@/constants/dataset'
import { actions, updateResultState } from '@/constants/common'
import { deepClone } from '@/utils/object'

let loading = false

const initQuery = { name: "", type: "", time: 0, offset: 0, limit: 20 }

const initState = {
  query: { ...initQuery },
  datasets: { items: [], total: 0, },
  versions: {},
  dataset: {},
  assets: { items: [], total: 0, },
  asset: { annotations: [], },
  allDatasets: [],
  publicDatasets: [],
}

export default {
  namespace: "dataset",
  state: deepClone(initState),
  effects: {
    *getDatasetGroups({ payload }, { call, put }) {
      const { pid, query } = payload
      const { code, result } = yield call(getDatasetGroups, pid, query)
      if (code === 0) {
        const groups = result.items.map(item => transferDatasetGroup(item))
        const payload = { items: groups, total: result.total }
        yield put({
          type: "UPDATE_DATASETS",
          payload,
        })
        return payload
      }
    },
    *batchDatasets({ payload }, { call, put }) {
      const { code, result } = yield call(batchDatasets, payload)
      if (code === 0) {
        const datasets = result.map(ds => transferDataset(ds))
        return datasets || []
      }
    },
    *getDataset({ payload }, { call, put, select }) {
      const { id, force } = payload
      if (!force) {
        const dataset = yield select(state => state.dataset.dataset[id])
        if (dataset) {
          return dataset
        }
      }
      const { code, result } = yield call(getDataset, id)
      if (code === 0) {
        const dataset = transferDataset(result)

        if (dataset.projectId) {
          const presult = yield put.resolve({
            type: 'project/getProject',
            payload: { id: dataset.projectId },
          })
          if (presult) {
            dataset.project = presult
          }
        }
        yield put({
          type: "UPDATE_DATASET",
          payload: { id: dataset.id, dataset },
        })
        return dataset
      }
    },
    *getDatasetVersions({ payload }, { select, call, put }) {
      const { gid, force } = payload
      if (!force) {
        const versions = yield select(({ dataset }) => dataset.versions)
        if (versions[gid]) {
          return versions[gid]
        }
      }
      const { code, result } = yield call(getDatasetByGroup, gid)
      if (code === 0) {
        const vss = result.items.map(item => transferDataset(item))
        const vs = { id: gid, versions: vss, }
        yield put({
          type: "UPDATE_VERSIONS",
          payload: vs,
        })
        return vss
      }
    },
    *queryDatasets({ payload }, { select, call, put }) {
      const { code, result } = yield call(queryDatasets, payload)
      if (code === 0) {
        return { items: result.items.map(ds => transferDataset(ds)), total: result.total }
      }
    },
    *getHiddenList({ payload }, { put }) {
      const query = { ...{ order_by: 'update_datetime' }, ...payload, visible: false }
      return yield put({
        type: 'queryDatasets',
        payload: query,
      })
    },
    *queryAllDatasets({ payload }, { select, call, put }) {
      if (loading) {
        return
      }
      loading = true
      const { pid, force } = payload
      if (!force) {
        const dssCache = yield select(state => state.dataset.allDatasets)
        if (dssCache.length) {
          loading = false
          return dssCache
        }
      }
      const dss = yield put.resolve({ type: 'queryDatasets', payload: { project_id: pid, state: states.VALID, limit: 10000 } })
      if (dss) {
        yield put({
          type: "UPDATE_ALL_DATASETS",
          payload: dss.items,
        })
        loading = false
        return dss.items
      }
      loading = false
    },
    *getAssetsOfDataset({ payload }, { call, put }) {
      const { code, result } = yield call(getAssetsOfDataset, payload)
      if (code === 0) {
        yield put({
          type: "UPDATE_ASSETS",
          payload: result,
        })
        return result
      }
    },
    *getAsset({ payload }, { call, put }) {
      const { code, result } = yield call(getAsset, payload.id, payload.hash)
      if (code === 0) {
        yield put({
          type: "UPDATE_ASSET",
          payload: result,
        })
        return result
      }
    },
    *delDataset({ payload }, { call, put }) {
      const { code, result } = yield call(delDataset, payload)
      if (code === 0) {
        yield put({
          type: "UPDATE_DATASET",
          payload: { id: payload, dataset: null },
        })
        return result
      }
    },
    *delDatasetGroup({ payload }, { call, put }) {
      const { code, result } = yield call(delDatasetGroup, payload)
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
    *createDataset({ payload }, { call, put }) {
      const { code, result } = yield call(createDataset, payload)
      if (code === 0) {
        return result
      }
    },
    *updateDataset({ payload }, { call, put }) {
      const { id, name } = payload
      const { code, result } = yield call(updateDataset, id, name)
      if (code === 0) {
        return result
      }
    },
    *getInternalDataset({ payload }, { call, put }) {
      const { code, result } = yield call(getInternalDataset, payload)
      if (code === 0) {
        const dss = result.items.map(item => transferDataset(item))
        const ds = { items: dss, total: result.total }
        yield put({
          type: "UPDATE_PUBLICDATASETS",
          payload: ds,
        })
        return ds
      }
    },
    *updateDatasets({ payload }, { put, select }) {
      const versions = yield select(state => state.dataset.versions)
      const tasks = payload || {}
      Object.keys(versions).forEach(gid => {
        const datasets = versions[gid]
        let updatedDatasets = datasets.map(dataset => {
          const updatedDataset = updateResultState(dataset, tasks)
          return updatedDataset ? { ...updatedDataset } : dataset
        })
        versions[gid] = updatedDatasets
      })
      yield put({
        type: 'UPDATE_ALL_VERSIONS',
        payload: { ...versions },
      })
      return { ...versions }
    },
    *updateDatasetState({ payload }, { put, select }) {
      const datasetCache = yield select(state => state.dataset.dataset)
      const tasks = payload || {}
      Object.keys(datasetCache).forEach(did => {
        const dataset = datasetCache[did]
        const updatedDataset = updateResultState(dataset, tasks)
        datasetCache[did] = updatedDataset ? updatedDataset : dataset
      })

      yield put({
        type: 'UPDATE_ALL_DATASET',
        payload: { ...datasetCache },
      })
    },
    *getHotDatasets({ payload }, { call, put }) {
      const { code, result } = yield call(getStats, { ...payload, q: 'ds' })
      let datasets = []
      if (code === 0) {
        const refs = {}
        const ids = result.map(item => {
          refs[item[0]] = item[1]
          return item[0]
        })
        if (ids.length) {
          const datasetsObj = yield put.resolve({ type: 'batchDatasets', payload: ids })
          if (datasetsObj) {
            datasets = datasetsObj.map(dataset => {
              dataset.count = refs[dataset.id]
              return dataset
            })
          }
        }
      }
      return datasets
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
    *compare({ payload }, { call, put }) {
      const { code, result } = yield call(evaluate, payload)
      if (code === 0) {
        return result
      }
    },
  },
  reducers: {
    UPDATE_DATASETS(state, { payload }) {
      return {
        ...state,
        datasets: payload
      }
    },
    UPDATE_ALL_DATASETS(state, { payload }) {
      return {
        ...state,
        allDatasets: payload
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
    UPDATE_DATASET(state, { payload }) {
      const { id, dataset } = payload
      const dss = { ...state.dataset, [id]: dataset, }
      return {
        ...state,
        dataset: dss,
      }
    },
    UPDATE_ALL_DATASET(state, { payload }) {
      const dataset = payload
      return {
        ...state,
        dataset,
      }
    },
    UPDATE_ASSETS(state, { payload }) {
      return {
        ...state,
        assets: payload
      }
    },
    UPDATE_ASSET(state, { payload }) {
      return {
        ...state,
        asset: payload
      }
    },
    UPDATE_PUBLICDATASETS(state, { payload }) {
      return {
        ...state,
        publicDatasets: payload
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
