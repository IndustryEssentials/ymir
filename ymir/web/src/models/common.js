import {
  getHistory,
  getStats,
  getSysInfo,
} from "@/services/common"

export default {
  namespace: "common",
  state: {
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
  },
  reducers: {
  },
}
