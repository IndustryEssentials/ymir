import {
  getKeywords,
  getHistory,
  getRuntimes,
  getStats,
} from "@/services/common"

export default {
  namespace: "common",
  state: {
    keywords: [],
  },
  effects: {
    *getKeywords({ payload }, { call, put, select }) {
      const keywords = yield select(({ common }) => common.keywords)
      if (keywords.length) {
        return
      }
      let { code, result } = yield call(getKeywords, payload)
      if (code === 0) {
        result.sort()
        yield put({
          type: "UPDATE_KEYWORDS",
          payload: result,
        })
        return result
      }
    },
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
    *getRuntimes({payload}, { call }) {
      const { code, result } = yield call(getRuntimes, payload)
      if (code === 0) {
        return result[0]
      }
    },
  },
  reducers: {
    UPDATE_KEYWORDS(state, { payload }) {
      return {
        ...state,
        keywords: payload,
      }
    },
  },
}
