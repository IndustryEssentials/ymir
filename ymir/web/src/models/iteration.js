import {
  getIterations,
  getIteration,
  createIterations,
  updateIteration,
} from "@/services/iteration"
import { transferIteration } from "@/constants/project"

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
      const id = payload
      const { code, result } = yield call(getIteration, id)
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
    *createIterations({ payload }, { call, put }) {
      const { code, result } = yield call(createIterations, payload)
      if (code === 0) {
        return result
      }
    },
    *updateIteration({ payload }, { call, put }) {
      const { id, ...params } = payload
      const { code, result } = yield call(updateIteration, id, params)
      if (code === 0) {
        return result
      }
    },
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
