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
  importDataset,
} from "@/services/dataset"

export default {
  namespace: "dataset",
  state: {
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
      }
      return result
    },
    *batchDatasets({ payload }, { call, put }) {
      const { code, result } = yield call(batchDatasets, payload)
      if (code === 0) {
        return result.items
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
      }
      return result
    },
    *getAsset({ payload }, { call, put }) {
      const { code, result } = yield call(getAsset, payload.id, payload.hash)
      if (code === 0) {
        yield put({
          type: "UPDATE_ASSET",
          payload: result,
        })
      }
      return result
    },
    *delDataset({ payload }, { call, put }) {
      const { code, result } = yield call(delDataset, payload)
      // if (code === 0) {
      //   yield put({
      //     type: "UPDATE_DATASETS",
      //     payload: result,
      //   })
      // }
      return result
    },
    *createDataset({ payload }, { call, put }) {
      const { code, result } = yield call(createDataset, payload)
      // if (code === 0) {
      //   yield put({
      //     type: "UPDATE_DATASETS",
      //     payload: result,
      //   })
      // }
      return result
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
      }
      return result
    },
    *importDataset({ payload }, { call, put }) {
      const { code, result } = yield call(importDataset, payload)
      // if (code === 0) {
      //   yield put({
      //     type: "UPDATE_DATASETS",
      //     payload: result,
      //   })
      // }
      return result
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
  },
}
