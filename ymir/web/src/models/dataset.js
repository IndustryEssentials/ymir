import { 
  getDatasets, 
  getDataset,
  batchDatasets,
  getAssetsOfDataset,
  getAsset,
  delDataset,
  createDataset,
  updateDataset,
  getInternalDataset,
} from "@/services/dataset"
import { getStats } from "../services/common"
import { isFinalState } from '@/constants/task'

const initQuery = {
  name: "",
  type: "",
  time: 0,
  offset: 0,
  limit: 20,
}

export default {
  namespace: "dataset",
  state: {
    query: initQuery,
    datasets: {
      items: [],
      total: 0,
    },
    dataset: {},
    assets: {
      items: [],
      total: 0,
    },
    asset: {
      annotations: [],
    },
    publicDatasets: [],
  },
  effects: {
    *getDatasets({ payload }, { call, put }) {
      const { code, result } = yield call(getDatasets, payload)
      if (code === 0) {
        yield put({
          type: "UPDATE_DATASETS",
          payload: result,
        })
        return result
      }
    },
    *batchDatasets({ payload }, { call, put }) {
      const { code, result } = yield call(batchDatasets, payload)
      if (code === 0) {
        return result
      }
    },
    *getDataset({ payload }, { call, put }) {
      const { code, result } = yield call(getDataset, payload)
      if (code === 0) {
        yield put({
          type: "UPDATE_DATASET",
          payload: result,
        })
        return result
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
    UPDATE_DATASET(state, { payload }) {
      return {
        ...state,
        dataset: payload
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
