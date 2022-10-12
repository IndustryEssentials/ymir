import {
  getHistory,
  getStats,
  getSysInfo,
} from "@/services/common"

export default {
  namespace: "common",
  state: {
    loading: true,
  },
  effects: {
    *getHistory({ payload }, { call }) {
      const { code, result } = yield call(getHistory, payload)
      if (code === 0) {
        return result
      }
    },
    *getStats({payload}, { call }) {
      const { code, result } = yield call(getStats, payload)
      if (code === 0) {
        return result
      }
    },
    *getSysInfo({}, { call }) {
      const { code, result } = yield call(getSysInfo)
      if (code === 0) {
        return result
      }
    },
    *setLoading({ payload }, { put }) {
      yield put({
        type: 'SET_LOADING',
        payload,
      })
    },
    *updateResultState({ payload }, { put }) {
      const { result, tasks } = payload
      const action = 'dataset/getDataset'
      
    },
  },
  reducers: {
    SET_LOADING (state, { payload }) {
      return {
        ...state,
        loading: payload,
      }
    }
  },
}
