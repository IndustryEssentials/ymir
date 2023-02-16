import { transferInferDataset } from '@/constants/dataset'
import { NormalReducer } from './_utils'
import { TASKTYPES } from '@/constants/task'

const reducers = {
  UPDATE_DATASETS: NormalReducer('datasets'),
}

const Pred = {
  namespace: 'pred',
  state: {
    datasets: { items: [], total: 0 },
  },
  effects: {
    *queryInferDatasets({ payload }, { call, put }) {
      const { pid } = payload
      const result = yield put.resolve({
        type: 'queryDatasets',
        payload: { ...payload, type: TASKTYPES.INFERENCE },
      })
      if (result) {
        const { items: datasets = [], total } = result
        const getIds = (key) => {
          const ids = datasets
            .map((ds) => {
              const param = ds.task?.parameters || {}
              return param[key]
            })
            .filter((notEmpty) => notEmpty)
          return [...new Set(ids)]
        }
        const modelIds = getIds('model_id')
        const datasetIds = getIds('dataset_id')
        yield put({
          type: 'model/batchLocalModels',
          payload: modelIds,
        })
        yield put({
          type: 'batchLocalDatasets',
          payload: { pid, ids: datasetIds },
        })
        return {
          items: datasets.map(transferInferDataset),
          total,
        }
      }
    },
    *getHiddenList({ payload }, { put }) {
      const query = { order_by: 'update_datetime', ...payload, type: TASKTYPES.INFERENCE, visible: false }
      return yield put({
        type: 'dataset/queryDatasets',
        payload: query,
      })
    },
    *restore({ payload: { pid, ids = [] } }, { put }) {
      return yield put({
        type: 'dataset/restore',
        payload: { pid, ids },
      })
    },
  },
  reducers: {
    ...reducers,
  },
}

export default Pred
