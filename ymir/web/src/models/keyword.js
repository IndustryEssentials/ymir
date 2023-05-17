import { 
  getKeywords, 
  updateKeyword,
  updateKeywords,
  getRecommendKeywords,
  checkDuplication,
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
    *checkDuplication({ payload: keywords }, { call, put }) {
      const { code, result } = yield call(checkDuplication, keywords)
      if (code === 0) {
        const newer = keywords.filter(kw => !result.includes(kw))
        return {dup: result, newer }
      }
    },
    *updateKeyword({ payload }, { call, put }) {
      const { code, result } = yield call(updateKeyword, payload)
      if (code === 0) {
        return result
      }
    },
    *getRecommendKeywords({ payload }, { call, put }) {
      const { code, result } = yield call(getRecommendKeywords, payload)
      if (code === 0) {
        return result.map(item => item.legend)
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
