import { 
  getModels, 
  batchModels,
  getModel,
  delModel,
  createModel,
  updateModel,
  verify,
} from "@/services/model"

export default {
  namespace: "model",
  state: {
    models: {
      items: [],
      total: 0,
    },
    model: {},
  },
  effects: {
    *getModels({ payload }, { call, put }) {
      const { code, result } = yield call(getModels, payload)
      if (code === 0) {
        yield put({
          type: "UPDATE_MODELS",
          payload: result,
        })
      }
      return result
    },
    *batchModels({ payload }, { call, put }) {
      const { code, result } = yield call(batchModels, payload)
      if (code === 0) {
        return result.items
      }
    },
    *getModel({ payload }, { call, put }) {
      const { code, result } = yield call(getModel, payload)
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
          type: "UPDATE_MODEL",
          payload: result,
        })
      }
      return result
    },
    *delModel({ payload }, { call, put }) {
      const { code, result } = yield call(delModel, payload)
      return result
    },
    *createModel({ payload }, { call, put }) {
      const { code, result } = yield call(createModel, payload)
      if (code === 0) {
        return result
      }
    },
    *updateModel({ payload }, { call, put }) {
      const { id, name } = payload
      const { code, result } = yield call(updateModel, id, name)
      if (code === 0) {
        return result
      }
    },
    *verify({ payload }, { call }) {
      const { id, urls, image } = payload
      const { code, result } = yield call(verify, id, urls, image)
      if (code === 0) {
        return result
      }
    },
  },
  reducers: {
    UPDATE_MODELS(state, { payload }) {
      return {
        ...state,
        models: payload
      }
    },
    UPDATE_MODEL(state, { payload }) {
      return {
        ...state,
        model: payload
      }
    },
  },
}
