import {
  getIterations,
  getIteration,
  createIteration,
  updateIteration,
  getMiningStats,
} from "@/services/iteration"
import { Stages, transferIteration, transferMiningStats } from "@/constants/iteration"
import { updateResultState } from '@/constants/common'

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
    currentStageResult: {},
    prepareStagesResult: {},
    actionPanelExpand: true,
  },
  effects: {
    *getIterations({ payload }, { call, put }) {
      const { id, more } = payload
      const { code, result } = yield call(getIterations, id)
      if (code === 0) {
        let iterations = result.map((iteration) => transferIteration(iteration))
        if (more && iterations.length) {
          yield put.resolve({
            type: 'moreIterationsInfo',
            payload: { iterations, id },
          })
        }
        yield put({
          type: "UPDATE_ITERATIONS",
          payload: { id, iterations },
        })
        // cache single iteration
        yield put({
          type: 'updateLocalIterations',
          payload: iterations,
        })
        return iterations
      }
    },
    *getIteration({ payload }, { call, put, select }) {
      const { pid, id, more } = payload
      let iteration = null
      // try get iteration from cache
      const cache = yield select(({ iteration }) => iteration.iteration[id])
      if (cache) {
        iteration = cache
      } else {
        iteration = yield put.resolve({
          type: 'getRemoteIteration',
          payload: { pid, id }
        })
      }
      if (iteration && more) {
        yield put.resolve({
          type: 'moreIterationsInfo',
          payload: { iterations: [iteration], id: pid },
        })
      }
      yield put({
        type: "UPDATE_ITERATION",
        payload: iteration,
      })
      return iteration
    },
    *getRemoteIteration({ payload }, { call }) {
      const { pid, id } = payload
      const { code, result } = yield call(getIteration, pid, id)
      if (code === 0) {
        return transferIteration(result)
      }
    },
    *moreIterationsInfo({ payload: { iterations, id } }, { put }) {
      if (!iterations.length) {
        return
      }
      const datasetIds = [...new Set(iterations.map(i => [
        i.wholeMiningSet,
        i.miningSet,
        i.miningResult,
        i.labelSet,
        i.trainUpdateSet,
        i.testSet,
      ]).flat())].filter(id => id)
      const modelIds = [...new Set(iterations.map(i => i.model))].filter(id => id)
      let datasets = []
      let models = []
      if (datasetIds?.length) {
        datasets = yield put.resolve({
          type: 'dataset/batchLocalDatasets',
          payload: { pid: id, ids: datasetIds },
        })
      }
      if (modelIds?.length) {
        models = yield put.resolve({
          type: 'model/batchLocalModels',
          payload: modelIds,
        })
      }
    },
    *getMiningStats({ payload }, { call, put }) {
      const { pid, id } = payload
      const { code, result } = yield call(getMiningStats, pid, id)
      if (code === 0) {
        return transferMiningStats(result)
      }
    },
    *getPrepareStagesResult({ payload }, { put }) {

      const project = yield put.resolve({
        type: 'project/getProject',
        payload,
      })

      if (project.candidateTrainSet) {
        yield put.resolve({
          type: 'dataset/getDataset',
          payload: { id: project.candidateTrainSet, }
        })
      }

      yield put.resolve({
        type: 'dataset/updateLocalDatasets',
        payload: [project.testSet, project.miningSet],
      })

      if (project.model) {
        yield put.resolve({
          type: 'model/getModel',
          payload: { id: project.model, }
        })
      }
      return true
    },
    *setCurrentStageResult({ payload }, { call, put }) {
      const result = payload
      if (result) {
        yield put({ type: 'UPDATE_CURRENT_STAGE_RESULT', payload: result })
        return result
      }
    },
    *createIteration({ payload }, { call, put, select }) {
      const { projectId } = payload
      const { code, result } = yield call(createIteration, payload)
      if (code === 0) {
        const iteration = transferIteration(result)
        yield put({
          type: 'updateLocalIterations',
          payload: [iteration],
        })
        const iterations = yield select(({ iteration }) => iteration.iterations[projectId])
        yield put({
          type: 'UPDATE_ITERATIONS',
          payload: { id: projectId, iterations: [...iterations, iteration] },
        })
        return iteration
      }
    },
    *updateIteration({ payload }, { call, put, select }) {
      const { id, ...params } = payload
      const { code, result } = yield call(updateIteration, id, params)
      if (code === 0) {
        const iteration = transferIteration(result)
        yield put({
          type: 'updateLocalIterations',
          payload: [{ ...iteration, needReload: true }],
        })
        const iterations = yield select(({ iteration: it }) => it.iterations[iteration.projectId])
        yield put({
          type: 'UPDATE_ITERATIONS',
          payload: { id: iteration.projectId, iterations: iterations.map(it => it.id === iteration.id ? iteration : it) },
        })
        return iteration
      }
    },
    *getStageResult({ payload }, { call, put }) {
      const { id, stage, force } = payload
      const isModel = stage === Stages.training
      const type = isModel ? 'model/getModel' : 'dataset/getDataset'
      const result = yield put.resolve({
        type,
        payload: { id, force },
      })
      return result
    },
    *updateLocalIterations({ payload: iterations = [] }, { put, select }) {
      for (let i = 0; i < iterations.length; i++) {
        const iteration = iterations[i];
        yield put({
          type: 'UPDATE_ITERATION',
          payload: iteration,
        })
      }
    },
    *updateIterationCache({ payload: tasks = {} }, { put, select }) {
      // const tasks = payload || {}
      const iteration = yield select(state => state.iteration.iteration)
      const updateItertion = Object.keys(iteration).reduce((prev, key) => {
        let item = iteration[key]
        if (item.id) {
          item = updateResultState(item, tasks)
        }
        return {
          ...prev,
          [key]: item,
        }
      }, {})
      yield put({
        type: 'UPDATE_ITERATION',
        payload: updateItertion,
      })
    },
    *toggleActionPanel({ payload }, { call, put, select }) {
      yield put.resolve({
        type: 'UPDATE_ACTIONPANELEXPAND',
        payload,
      })
    },
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
      const cache = state.iteration
      return {
        ...state,
        iteration: {
          ...cache,
          [iteration.id]: iteration,
        },
      }
    },
    UPDATE_CURRENT_STAGE_RESULT(state, { payload }) {
      return {
        ...state,
        currentStageResult: payload,
      }
    },
    UPDATE_PREPARE_STAGES_RESULT(state, { payload }) {
      const { pid, results } = payload
      return {
        ...state,
        prepareStagesResult: {
          ...state.prepareStagesResult,
          [pid]: results,
        },
      }
    },
    UPDATE_ACTIONPANELEXPAND(state, { payload }) {
      return {
        ...state,
        actionPanelExpand: payload,
      }
    }
  },
}
