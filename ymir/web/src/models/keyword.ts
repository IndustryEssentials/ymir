import { Classes } from '@/constants'
import { getKeywords, updateKeyword, updateKeywords, getRecommendKeywords, checkDuplication } from '@/services/keyword'
import { KeywordState, KeywordStore } from '.'
import { createEffect, createReducersByState } from './_utils'

const state: KeywordState = {
  allKeywords: [],
  reload: true,
}

const KeywordModel: KeywordStore = {
  namespace: 'keyword',
  state,
  effects: {
    getAllKeywords: createEffect(function* ({}, { put, select }) {
      const { reload, allKeywords } = yield select(({ keyword }) => keyword)
      if (!reload) {
        return allKeywords
      }
      const result = yield put.resolve({
        type: 'getKeywords',
        payload: { limit: 100000 },
      })
      if (result) {
        const { items } = result
        yield put({
          type: 'UpdateAllKeywords',
          payload: items,
        })
        yield put({
          type: 'UpdateReload',
          payload: false,
        })
        return items
      }
    }),
    getKeywords: createEffect(function* ({ payload }, { call, put }) {
      const { code, result } = yield call(getKeywords, payload)
      if (code === 0) {
        return result
      }
    }),
    updateKeywords: createEffect(function* ({ payload }, { call, put }) {
      const { code, result } = yield call(updateKeywords, payload)
      if (code === 0) {
        yield put({
          type: 'UpdateReload',
          payload: true,
        })
        return result
      }
    }),
    checkDuplication: createEffect<Classes>(function* ({ payload: keywords }, { call, put }) {
      const { code, result } = yield call(checkDuplication, keywords)
      if (code === 0) {
        const newer = keywords.filter((kw) => !result.includes(kw))
        return { dup: result, newer }
      }
    }),
    updateKeyword: createEffect(function* ({ payload }, { call, put }) {
      const { code, result } = yield call(updateKeyword, payload)
      if (code === 0) {
        yield put({
          type: 'UpdateReload',
          payload: true,
        })
        return result
      }
    }),
    getRecommendKeywords: createEffect(function* ({ payload }, { call, put }) {
      const { code, result } = yield call(getRecommendKeywords, payload)
      if (code === 0) {
        return result.map((item: { legend: string }) => item.legend)
      }
    }),
  },
  reducers: createReducersByState(state),
}

export default KeywordModel
