import { 
  getKeywords, 
  updateKeyword,
  updateKeywords,
  getRecommendKeywords,
} from "@/services/keyword"

export default {
  namespace: "keyword",
  state: {
    keywords: {
      items: [],
      total: 0,
    },
    keyword: {},
  },
  effects: {
    *getKeywords({ payload }, { call, put }) {
      const { code, result } = yield call(getKeywords, payload)
      if (code === 0) {
        yield put({
          type: "UPDATE_KEYWORDS",
          payload: result,
        })
        return result
      }
    },
    *updateKeywords({ payload }, { call, put }) {
      const { code, result } = yield call(updateKeywords, payload)
      if (code === 0) {
        return result
      }
    },
    *updateKeyword({ payload }, { call, put }) {
      const { code, result } = yield call(updateKeyword, payload)
      if (code === 0) {
        return result
      }
    },
    *getRecommendKeywords({ payload }, { call, put }) {
      const data = yield call(getRecommendKeywords, payload)
      if (data.code === 0) {
        return data.result.map(item => item[0])
      }
    }
  },
  reducers: {
    UPDATE_KEYWORDS(state, { payload }) {
      return {
        ...state,
        keywords: payload
      }
    },
    UPDATE_KEYWORD(state, { payload }) {
      return {
        ...state,
        keyword: payload
      }
    },
  },
}
