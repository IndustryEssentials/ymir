import { createReducers } from './_utils'

type ReducerType = {
  name: string,field: string,
}

const reducersList: ReducerType[] = [
  { name: 'UpdatePredictions', field: 'predictions' },
  { name: 'UpdatePrediction', field: 'prediction' },
]

const PredictionModel: YStates.PredictionStore = {
  namespace: 'prediction',
  state: {
    predictions: { items: [], total: 0 },
    prediction: {},
  },
  effects: {
    getList: () => {},
  },
  reducers: createReducers(reducersList),
}

export default PredictionModel
