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
      const id = payload
      const { code, result } = yield call(getIterations, id)
      if (code === 0) {
        const iterations = result.map((iteration) =>
          transferIteration(iteration)
        )
        yield put({
          type: "UPDATE_ITERATIONS",
          payload: { id, iterations },
        })
        return iterations
      }
    },
    *getIteration({ payload }, { call, put }) {
      const { pid, id } = payload
      const { code, result } = yield call(getIteration, pid, id)
      if (code === 0) {
        const iteration = transferIteration(result)
        console.log("get from remote iteration: ", iteration)
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
      const type = stage === Stages.training ? 'model/getModel' : 'dataset/getDataset'
      const result = yield put.resolve({
        type,
        payload: id,
      })
      if (result) {
        return result
      }
    }
  },
  reducers: {
    UPDATE_ITERATIONS(state, { payload }) {
      const projectIterations = { ...state.iterations }
      const { id, iterations } = payload
      projectIterations[id] = iterations
      console.log("iteration reducer: ", id, iterations)
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
