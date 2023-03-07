import {
  getStats,
  getSysInfo,
} from "@/services/common"
import { actions, updateResultByTask, ResultStates } from '@/constants/common'

export default {
  namespace: "common",
  state: {
    loading: true,
  },
  effects: {
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
