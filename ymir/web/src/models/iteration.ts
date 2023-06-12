import { getIterations, getIteration, createIteration, getMiningStats, bindStep, unbindStep, nextStep } from '@/services/iteration'
import { Stages, transferIteration, transferMiningStats } from '@/constants/iteration'
import { createEffect, createReducersByState } from './_utils'
import { IterationState, IterationStore } from '.'
import { Backend, Iteration, Project } from '@/constants'
import { CreateParams } from '@/services/typings/iteration'

const state: IterationState = {
  iterations: {},
  iteration: {},
  actionPanelExpand: true,
}

const IterationModel: IterationStore = {
  namespace: 'iteration',
  state,
  effects: {
    getIterations: createEffect<{ id: number; more?: boolean }>(function* ({ payload }, { call, put }) {
      const { id, more } = payload
      const { code, result } = yield call(getIterations, id)
      if (code === 0) {
        let iterations = (result as Backend[]).map(transferIteration)
        if (more && iterations.length) {
          yield put.resolve({
            type: 'moreIterationsInfo',
            payload: { iterations, id },
          })
        }
        yield put({
          type: 'UpdateIterations',
          payload: { [id]: iterations },
        })
        // cache single iteration
        yield put({
          type: 'updateLocalIterations',
          payload: iterations,
        })
        return iterations
      }
    }),
    getIteration: createEffect<{ pid: number; id: number; more?: boolean }>(function* ({ payload }, { call, put, select }) {
      const { pid, id, more } = payload
      let iteration = null
      // try get iteration from cache
      const cache: Iteration = yield select(({ iteration }) => iteration.iteration[id])
      if (cache) {
        iteration = cache
      } else {
        iteration = yield put.resolve({
          type: 'getRemoteIteration',
          payload: { pid, id },
        })
      }
      if (iteration && more) {
        yield put.resolve({
          type: 'moreIterationsInfo',
          payload: { iterations: [iteration], id: pid },
        })
      }
      yield put({
        type: 'UpdateIteration',
        payload: { [iteration.id]: iteration },
      })
      return iteration
    }),
    getRemoteIteration: createEffect<{ pid: number; id: number }>(function* ({ payload }, { call }) {
      const { pid, id } = payload
      const { code, result } = yield call(getIteration, pid, id)
      if (code === 0) {
        return transferIteration(result)
      }
    }),
    moreIterationsInfo: createEffect<{ id: number; iterations: Iteration[] }>(function* ({ payload: { iterations, id } }, { put }) {
      if (!iterations.length) {
        return
      }
      const getIds = (iterations: Iteration[], type = 'dataset') =>
        [
          ...new Set(
            iterations
              .map(({ wholeMiningSet, testSet, steps }) => {
                const stepResults = steps.filter((step) => step.resultType === type).map((step) => step.resultId)
                return type === 'dataset' ? [wholeMiningSet, testSet, ...stepResults] : stepResults
              })
              .flat(),
          ),
        ].filter((id) => id)
      const datasetIds = getIds(iterations)
      const modelIds = getIds(iterations, 'model')
      if (datasetIds?.length) {
        yield put({
          type: 'dataset/batchLocalDatasets',
          payload: { pid: id, ids: datasetIds },
        })
      }
      if (modelIds?.length) {
        yield put({
          type: 'model/batchLocalModels',
          payload: modelIds,
        })
      }
    }),
    updateTrainClasses: createEffect<{ id: number; classes: string[] }>(function* ({ payload: { id, classes } }, { call, put }) {
      return yield put({ type: 'project/updateProject', payload: { id, keywords: classes } })
    }),
    getMiningStats: createEffect<{ pid: number; id: number }>(function* ({ payload }, { call, put }) {
      const { pid, id } = payload
      const { code, result } = yield call(getMiningStats, pid, id)
      if (code === 0) {
        return transferMiningStats(result)
      }
    }),
    getPrepareStagesResult: createEffect<number>(function* ({ payload }, { put }) {
      const project: Project = yield put.resolve({
        type: 'project/getProject',
        payload,
      })

      if (project.candidateTrainSet) {
        yield put.resolve({
          type: 'dataset/getDataset',
          payload: { id: project.candidateTrainSet },
        })
      }

      yield put.resolve({
        type: 'dataset/updateLocalDatasets',
        payload: [project.testSet, project.miningSet],
      })

      if (project.model) {
        yield put.resolve({
          type: 'model/getModel',
          payload: { id: project.model },
        })
      }
      return true
    }),
    createIteration: createEffect<CreateParams>(function* ({ payload }, { call, put, select }) {
      const { projectId } = payload
      const { code, result } = yield call(createIteration, payload)
      if (code === 0) {
        const iteration = transferIteration(result)
        yield put({
          type: 'updateLocalIterations',
          payload: [iteration],
        })
        const iterations = yield select(({ iteration }) => iteration.iterations[projectId] || [])
        yield put({
          type: 'UpdateIterations',
          payload: { [projectId]: [...iterations, iteration] },
        })
        return iteration
      }
    }),
    getStageResult: createEffect(function* ({ payload }, { call, put }) {
      const { id, stage, force } = payload
      const isModel = stage === Stages.training
      const type = isModel ? 'model/getModel' : 'dataset/getDataset'
      const result = yield put.resolve({
        type,
        payload: { id, force },
      })
      return result
    }),
    updateLocalIterations: createEffect<Iteration[]>(function* ({ payload: iterations = [] }, { put, select }) {
      const objIterations = iterations.reduce(
        (prev, iteration) =>
          iteration?.id
            ? {
                ...prev,
                [iteration.id]: iteration,
              }
            : prev,
        {},
      )
      yield put({
        type: 'UpdateIteration',
        payload: objIterations,
      })
    }),
    toggleActionPanel: createEffect<boolean>(function* ({ payload }, { call, put, select }) {
      yield put.resolve({
        type: 'UPDATE_ACTIONPANELEXPAND',
        payload,
      })
    }),
    bindStep: createEffect<{ id: number; sid: number; tid: number }>(function* ({ payload }, { call, put, select }) {
      const { id, sid, tid } = payload
      const { code, result } = yield call(bindStep, id, sid, tid)
      if (code === 0) {
        return result
      }
    }),
    skipStep: createEffect<{ id: number; sid: number }>(function* ({ payload }, { call, put, select }) {
      const { id, sid } = payload
      const { code } = yield call(unbindStep, id, sid)
      if (code === 0) {
        const { code: skipCode, result } = yield call(nextStep, id, sid)
        if (skipCode === 0) {
          return result
        }
      }
    }),
    nextStep: createEffect<{ id: number; sid: number }>(function* ({ payload }, { call, put, select }) {
      const { id, sid } = payload
      const { code, result } = yield call(nextStep, id, sid)
      if (code === 0) {
        return result
      }
    }),
  },
  reducers: createReducersByState(state),
}

export default IterationModel
