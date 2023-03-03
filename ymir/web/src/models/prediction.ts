import { transferPrediction } from '@/constants/prediction'
import { getPrediction, getPredictions } from '@/services/prediction'
import { createEffect, createReducers, transferList } from './_utils'
type PredictionsPayload = { pid: number; force?: boolean; [key: string]: any }
type PredictionPayload = { id: number; verbose?: boolean; force?: boolean }

const reducersList = [
  { name: 'UpdatePredictions', field: 'predictions' },
  { name: 'UpdatePrediction', field: 'prediction' },
]

const PredictionModel: YStates.PredictionStore = {
  namespace: 'prediction',
  state: {
    predictions: {},
    prediction: {},
  },
  effects: {
    getPredictions: createEffect<PredictionsPayload>(function* ({ payload }, { call, select, put }) {
      const { pid, force, ...params } = payload
      if (!force) {
        const list: YStates.List<YModels.Prediction> = yield select(({ prediction }) => prediction.predictions[pid])
        if (list) {
          return list
        }
      }
      const { code, result } = yield call<YModels.ResponseResultList>(getPredictions, { pid, ...params })
      if (code === 0) {
        const predictions = transferList<YModels.Prediction>(result, transferPrediction)
        yield put({
          type: 'prediction/updatePredictions',
          payload: predictions,
        })
        return predictions
      }
    }),
    getPrediction: createEffect<PredictionPayload>(function* ({ payload }, { call, select, put }) {
      const { id, verbose, force } = payload
      if (!force) {
        const pred = yield select(({ prediction }) => prediction.prediction[id])
        if (pred) {
          return pred
        }
      }
      const { code, result } = yield call(getPrediction, id, verbose)
      if (code === 0) {
        const prediction = transferPrediction(result)

        if (prediction.projectId) {
          const presult = yield put.resolve<{ id: number }, YModels.Project>({
            type: 'project/getProject',
            payload: { id: prediction.projectId },
          })
          if (presult) {
            prediction.project = presult
          }
        }
        yield put({
          type: 'UPDATE_DATASET',
          payload: { id: prediction.id, prediction },
        })
        return prediction
      }
    }),
  },
  reducers: createReducers(reducersList),
}

export default PredictionModel
