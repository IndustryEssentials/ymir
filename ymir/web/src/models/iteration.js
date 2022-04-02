import {
  getIterations,
  getIteration,
  createIteration,
  updateIteration,
} from "@/services/iteration"
import { Stages, transferIteration } from "@/constants/project"


const initQuery = {
  name: "",
  offset: 0,
  limit: 20,
}

export default {
  namespace: "iteration",
  state: {
    query: initQuery,
    iterations: {},
    iteration: {},
  },
  effects: {
    *getIterations({ payload }, { call, put }) {
      const { id, more } = payload
      const { code, result } = yield call(getIterations, id)
      if (code === 0) {
        let iterations = result.map((iteration) => transferIteration(iteration))
        console.log('iterations:', iterations)
        if (more) {
          const datasetIds = [...new Set(iterations.map(i => [i.miningSet, i.miningResult, i.labelSet, i.trainUpdateSet]).flat())].filter(id => id)
          const modelIds = [...new Set(iterations.map(i => i.model))].filter(id => id)
          const datasets = yield put.resolve({
            type: 'dataset/batchDatasets',
            payload: datasetIds,
          })
          const models = yield put.resolve({
            type: 'model/batchModels',
            payload: modelIds,
          })
          iterations = iterations.map(i => {
            const ds = id => datasets.find(d => d.id === id)
            return {
              ...i,
              trainUpdateDataset: ds(i.trainUpdateSet),
              miningDataset: ds(i.miningSet),
              miningResultDataset: ds(i.miningResult),
              labelDataset: ds(i.labelSet),
              trainingModel: models.find(m => m.id === i.model),
            }
          })
        }
        yield put({
          type: "UPDATE_ITERATIONS",
          payload: { id, iterations },
        })
        console.log('return iterations:', iterations)
        return iterations
      }
    },
    *getIteration({ payload }, { call, put }) {
      const { pid, id } = payload
      const { code, result } = yield call(getIteration, pid, id)
      if (code === 0) {
        const iteration = transferIteration(result)
        yield put({
          type: "UPDATE_ITERATION",
          payload: iteration,
        })
        return iteration
      }
    },
    *createIteration({ payload }, { call, put }) {
      const { code, result } = yield call(createIteration, payload)
      if (code === 0) {
        return result
      }
    },
    *updateIteration({ payload }, { call, put }) {
      const { id, ...params } = payload
      const { code, result } = yield call(updateIteration, id, params)
      if (code === 0) {
        return transferIteration(result)
      }
    },
    *getStageResult({ payload }, { call, put }) {
      const { id, stage } = payload
      const isModel = stage === Stages.training
      const type = isModel ? 'model/getModel' : 'dataset/getDataset'
      const result = yield put.resolve({
        type,
        payload: id,
      })
      if (result) {
        return {
          ...result,
        }
      }
    }
  },
  reducers: {
    UPDATE_ITERATIONS(state, { payload }) {
      const projectIterations = { ...state.iterations }
      const { id, iterations } = payload
      projectIterations[id] = iterations
      return {
        ...state,
        iterations: projectIterations,
      }
    },
    UPDATE_ITERATION(state, { payload }) {
      const iteration = payload
      return {
        ...state,
        iteration,
      }
    },
  },
}
