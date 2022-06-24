import {
  getVisualizations,
  delVisualization,
  createVisualization,
} from "@/services/visualization"
import { transferVisualization } from '@/constants/visualization'
import { deepClone } from '@/utils/object'

const initQuery = {
  name: "",
  offset: 0,
  limit: 20,
}
const initState = {
  query: initQuery,
  list: {
    items: [],
    total: 0,
  },
  projects: {},
}

export default {
  namespace: "visualization",
  state: deepClone(initState),
  effects: {
    *getVisualizations({ payload }, { call, put }) {
      const { code, result } = yield call(getVisualizations, payload)
      if (code === 0) {
        const visualizations = { items: result?.items?.map(visualization => transferVisualization(visualization)), total: result.total }
        yield put({
          type: "UPDATE_LIST",
          payload: visualizations,
        })
        return visualizations
      }
    },
    *delVisualization({ payload }, { call, put }) {
      const { code, result } = yield call(delVisualization, payload)
      if (code === 0) {
        return result
      }
    },
    *createVisualization({ payload }, { call, put }) {
      const { code, result } = yield call(createVisualization, payload)
      if (code === 0) {
        return result
      }
    },
    *updateQuery({ payload = {} }, { put, select }) {
      const query = yield select(({ project }) => project.query)
      yield put({
        type: 'UPDATE_QUERY',
        payload: {
          ...query,
          ...payload,
          offset: query.offset === payload.offset ? initQuery.offset : payload.offset,
        }
      })
    },
    *resetQuery({ }, { put }) {
      yield put({
        type: 'UPDATE_QUERY',
        payload: initQuery,
      })
    },
    *clearCache({ }, { put }) {
      yield put({ type: 'CLEAR_ALL' })
    },
  },
  reducers: {
    UPDATE_LIST(state, { payload }) {
      return {
        ...state,
        list: payload
      }
    },
    UPDATE_QUERY(state, { payload }) {
      return {
        ...state,
        query: payload,
      }
    },
    CLEAR_ALL() {
      return deepClone(initState)
    },
  },
}
