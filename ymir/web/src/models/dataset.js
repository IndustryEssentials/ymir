import { 
  getDatasetGroups, getDatasetByGroup,  queryDatasets, getDataset, batchDatasets,
  getAssetsOfDataset, getAsset, delDataset, delDatasetGroup, createDataset, updateDataset, getInternalDataset,
} from "@/services/dataset"
import { getStats } from "../services/common"
import { isFinalState } from '@/constants/task'
import { transferDatasetGroup, transferDataset, states } from '@/constants/dataset'

const initQuery = { name: "", type: "", time: 0, offset: 0, limit: 20 }

export default {
  namespace: "dataset",
  state: {
    query: initQuery,
    datasets: { items: [], total: 0, },
    versions: {},
    dataset: {},
    assets: { items: [], total: 0, },
    asset: { annotations: [], },
    allDatasets: [],
    publicDatasets: [],
  },
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
    *getDataset({ payload }, { call, put }) {
      const { code, result } = yield call(getDataset, payload)
      if (code === 0) {
        const dataset = transferDataset(result)
        
        if (dataset.projectId) {
          const presult = yield put.resolve({
            type: 'project/getProject',
            payload: dataset.projectId,
          })
          if (presult) {
            dataset.project = presult
          }
        }
        yield put({
          type: "UPDATE_DATASET",
          payload: dataset,
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
        return vs
      }
    },
    *queryDatasets({ payload }, { select, call, put }) {
      const { code, result } = yield call(queryDatasets, payload)
      if (code === 0) {
        return { items: result.items.map(ds => transferDataset(ds)), total: result.total }
      }
    },
    *queryAllDatasets({ payload }, { select, call, put }) {
      const pid = payload
      const dss = yield put.resolve({ type: 'queryDatasets', payload: { project_id: pid, state: states.VALID, limit: 10000 }})
      if (dss) {
        yield put({
          type: "UPDATE_ALL_DATASETS",
          payload: dss.items,
        })
      }
    },
    
    *getKeywordRates({ payload }, { call, put }) {
      const id = payload
      const { code, result } = yield call(getAssetsOfDataset, { id, limit: 1 })
      if (code === 0) {
        const { total, keywords, negative_info } = result
        const { negative_images_cnt, project_negative_images_cnt } = result.negative_info
        return { keywords, total, negative: negative_images_cnt, negative_project: project_negative_images_cnt }
      }
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
        return result
      }
    },
    *delDatasetGroup({ payload }, { call, put }) {
      const { code, result } = yield call(delDatasetGroup, payload)
      if (code === 0) {
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
        yield put({
          type: "UPDATE_PUBLICDATASETS",
          payload: result,
        })
        return result
      }
    },
    *updateDatasets({ payload }, { put, select }) {
      const datasets = yield select(state => state.dataset.datasets)
      const updateList = payload || {}
      const result = datasets.items.map(dataset => {
        const updateItem = updateList[dataset.hash]
        if (updateItem) {
          dataset.state = updateItem.state
          dataset.progress = updateItem.percent * 100
          if (isFinalState(updateItem.state)) {
            dataset.forceUpdate = true
          }
        }
        return dataset
      })
      yield put({
        type: 'UPDATE_DATASETS',
        payload: { items: result, total: datasets.total },
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
    *resetQuery({}, { put }) {
      yield put({
        type: 'UPDATE_QUERY',
        payload: initQuery,
      })
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
        versions: vs,
      }
    },
    UPDATE_DATASET(state, { payload }) {
      const ds = payload
      const dss = { ...state.dataset, [ds.id]: ds, }
      return {
        ...state,
        dataset: dss,
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
  },
}
