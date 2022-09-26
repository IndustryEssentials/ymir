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
  },
  effects: {
    *getIterations({ payload }, { call, put }) {
      const { id, more } = payload
      const { code, result } = yield call(getIterations, id)
      if (code === 0) {
        let iterations = result.map((iteration) => transferIteration(iteration))
        if (more && iterations.length) {
          iterations = yield put.resolve({
            type: 'moreIterationsInfo',
            payload: { iterations, id },
          })
        }
        yield put({
          type: "UPDATE_ITERATIONS",
          payload: { id, iterations },
        })
        return iterations
      }
    },
    *getIteration({ payload }, { call, put }) {
      const { pid, id, more } = payload
      const { code, result } = yield call(getIteration, pid, id)
      if (code === 0) {
        let iteration = transferIteration(result)
        if (more) {
          [iteration] = yield put.resolve({
            type: 'moreIterationsInfo',
            payload: { iterations: [iteration], id: pid },
          })
        }
        yield put({
          type: "UPDATE_ITERATION",
          payload: iteration,
        })
        return iteration
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
          type: 'dataset/batchDatasets',
          payload: { pid: id, ids: datasetIds },
        })
      }
      if (modelIds?.length) {
        models = yield put.resolve({
          type: 'model/batchModels',
          payload: modelIds,
        })
      }
      const result = iterations.map(i => {
        const ds = id => datasets.find(d => d.id === id)
        return {
          ...i,
          wholeMiningDataset: ds(i.wholeMiningSet),
          trainUpdateDataset: ds(i.trainUpdateSet),
          miningDataset: ds(i.miningSet),
          miningResultDataset: ds(i.miningResult),
          labelDataset: ds(i.labelSet),
          testDataset: ds(i.testSet),
          trainingModel: models.find(m => m.id === i.model),
        }
      })
      return result
    },
    *getMiningStats({ payload }, { call, put }) {
      const { pid, id } = payload
      const { code, result } = yield call(getMiningStats, pid, id)
      if (code === 0) {
        return transferMiningStats(result)
      }
    },
    *getIterationStagesResult({ payload }, { put }) {
      const iteration = payload

      const fields = ['miningSet', 'miningResult', 'labelSet', 'trainUpdateSet']
      const datasetIds = fields.map(field => iteration[field]).filter(id => id)
      const modelId = iteration.model
      let datasets = []
      let model = []
      if (datasetIds?.length) {
        datasets = yield put.resolve({
          type: 'dataset/batchDatasets',
          payload: { pid: iteration.projectId, ids: datasetIds },
        })
      }
      if (modelId) {
        model = yield put.resolve({
          type: 'model/getModel',
          payload: { id: modelId },
        })
      }
      const ds = id => datasets.find(d => d.id === id)
      return {
        ...iteration,
        ...fields.reduce((prev, field) => ({ ...prev, [`i${field}`]: ds(iteration[field]) }), {}),
        imodel: model,
      }
    },
    *getPrepareStagesResult({ payload }, { put }) {
      const { id } = payload
      const project = yield put.resolve({
        type: 'project/getProject',
        payload,
      })
      const results = {
        testSet: project.testSet,
        miningSet: project.miningSet,
      }

      if (project.candidateTrainSet) {
        const candidateTrainSet = yield put.resolve({
          type: 'dataset/getDataset',
          payload: { id: project.candidateTrainSet, }
        })
        results.candidateTrainSet = candidateTrainSet
      }

      if (project.model) {
        const model = yield put.resolve({
          type: 'model/getModel',
          payload: { id: project.model, }
        })
        results.modelStage = model
      }

      yield put({
        type: 'UPDATE_PREPARE_STAGES_RESULT',
        payload: { pid: id, results },
      })

      return results
    },
    *setCurrentStageResult({ payload }, { call, put }) {
      const result = payload
      if (result) {
        yield put({ type: 'UPDATE_CURRENT_STAGE_RESULT', payload: result })
        return result
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
      const { id, stage, force } = payload
      const isModel = stage === Stages.training
      const type = isModel ? 'model/getModel' : 'dataset/getDataset'
      const result = yield put.resolve({
        type,
        payload: { id, force },
      })
      if (result) {
        yield put({ type: 'UPDATE_CURRENT_STAGE_RESULT', payload: result })
        return result
      }
    },
    *updateCurrentStageResult({ payload }, { put, select }) {
      const result = yield select(state => state.iteration.currentStageResult)
      const tasks = payload || {}
      const updated = updateResultState(result, tasks)

      if (updated) {
        yield put({
          type: 'UPDATE_CURRENT_STAGE_RESULT',
          payload: { ...updated },
        })
      }
    },
    *updatePrepareStagesResult({ payload }, { put, select }) {
      const { id } = yield select(({ project }) => project.current)
      const results = yield select(({ iteration }) => iteration.prepareStagesResult[id])
      const tasks = payload || {}
      const updatedResults = Object.keys(results || {}).reduce((prev, key) => {
        const result = results[key]
        const updated = result ? updateResultState(result, tasks) : undefined
        return { ...prev, [key]: updated }
      }, {})

      if (updatedResults) {
        yield put({
          type: 'UPDATE_PREPARE_STAGES_RESULT',
          payload: { pid: id, results: updatedResults },
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
  },
}
