import { 
  getMirror, 
  getMirrors,
  delMirror,
  createMirror,
  updateMirror,
} from "@/services/mirror"

export default {
  namespace: "mirror",
  state: {
    mirrors: {
      items: [],
      total: 0,
    },
    mirror: {},
  },
  effects: {
    *getMirrors({ payload }, { call, put }) {
      const { code, result } = yield call(getMirrors, payload)
      if (code === 0) {
        yield put({
          type: "UPDATE_MIRRORS",
          payload: result,
        })
      }
      return result
    },
    *batchMirrors({ payload }, { call, put }) {
      const { code, result } = yield call(batchMirrors, payload)
      if (code === 0) {
        return result.items
      }
    },
    *getMirror({ payload }, { call, put }) {
      const { code, result } = yield call(getMirror, payload)
      if (code === 0) {
        const pa = result.parameters || {}
        const trainSets = pa?.include_train_datasets || []
        const testSets = pa?.include_validation_datasets || []
        const ids = [
          ...trainSets,
          ...testSets,
        ]
        if (ids.length) {
          const datasets = yield put.resolve({ type: 'dataset/batchDatasets', payload: ids })
          if (datasets && datasets.length) {
            result['trainSets'] = trainSets.map(sid => datasets.find(ds => ds.id === sid))
            result['testSets'] = testSets.map(sid => datasets.find(ds => ds.id === sid))
          }
        }
        yield put({
          type: "UPDATE_MIRROR",
          payload: result,
        })
      }
      return result
    },
    *delMirror({ payload }, { call, put }) {
      const { code, result } = yield call(delMirror, payload)
      return result
    },
    *createMirror({ payload }, { call, put }) {
      const { code, result } = yield call(createMirror, payload)
      if (code === 0) {
        return result
      }
    },
    *updateMirror({ payload }, { call, put }) {
      const { id, name } = payload
      const { code, result } = yield call(updateMirror, id, name)
      if (code === 0) {
        return result
      }
    },
    *verify({ payload }, { call }) {
      const { id, urls } = payload
      console.log('mirror of mirrors: ', id, urls)
      const { code, result } = yield call(verify, id, urls)
      if (code === 0) {
        return result
      }
    },
  },
  reducers: {
    UPDATE_MIRRORS(state, { payload }) {
      return {
        ...state,
        mirrors: payload
      }
    },
    UPDATE_MIRROR(state, { payload }) {
      return {
        ...state,
        mirror: payload
      }
    },
  },
}
