import {
  getDatasetGroups,
  getDatasetByGroup,
  queryDatasets,
  getDataset,
  batchDatasets,
  analysis,
  batchAct,
  delDataset,
  delDatasetGroup,
  createDataset,
  updateDataset,
  getInternalDataset,
  getNegativeKeywords,
  updateVersion,
  checkDuplication,
} from '@/services/dataset'
import { transferDatasetGroup, transferDataset, transferDatasetAnalysis, transferAnnotationsCount } from '@/constants/dataset'
import { actions, updateResultState, updateResultByTask, ResultStates } from '@/constants/common'
import { createEffect, createReducersByState } from './_utils'
import { deepClone } from '@/utils/object'
import { TASKTYPES } from '@/constants/task'
import { DatasetState, DatasetStore } from '.'
import { List } from './typings/common'

const initQuery = { name: '', type: '', time: 0, current: 1, offset: 0, limit: 20 }

const list = [
  { name: 'UPDATE_ALL_DATASETS', field: 'allDatasets' },
  { name: 'UpdateValidDatasetCount', field: 'validDatasetCount' },
  { name: 'UpdateTrainingDatasetCount', field: 'trainingDatasetCount' },
  { name: 'UpdateVersions', field: 'versions' },
]

const initState = {
  query: { ...initQuery },
  datasets: {},
  versions: {},
  dataset: {},
  allDatasets: {},
  publicDatasets: [],
  validDatasetCount: 0,
  trainingDatasetCount: 0,
}

const reducers = createReducersByState<DatasetState>(initState)

const DatasetModal: DatasetStore = {
  namespace: 'dataset',
  state: deepClone(initState),
  effects: {
    getDatasetGroups: createEffect(function* ({ payload }, { call, put }) {
      const { pid, query } = payload
      const { code, result } = yield call(getDatasetGroups, pid, query)
      if (code === 0) {
        const groups = (result as List<YModels.BackendData>).items.map(transferDatasetGroup)
        const payload = { items: groups, total: result.total }
        yield put({
          type: 'UpdateDatasets',
          payload: { [pid]: payload },
        })
        for (let index = 0; index < groups.length; index++) {
          const group = groups[index]
          if (!group) {
            continue
          }
          yield put({
            type: 'UpdateVersions',
            payload: {
              [group.id]: group.versions,
            },
          })
        }
        return payload
      }
    }),
    batchLocalDatasets: createEffect<{ pid: number; ids: number[]; ck?: boolean }>(function* ({ payload }, { call, put }) {
      const { pid, ids, ck } = payload
      const cache: YModels.Dataset[] = yield put.resolve({
        type: 'getLocalDatasets',
        payload: ids,
      })
      const fixedCache = cache.filter((item) => !item.needReload)
      if (ids.length === fixedCache.length) {
        return cache
      }
      const fetchIds = ids.filter((id) => fixedCache.every((ds) => ds.id !== id))
      const remoteDatasets = yield put.resolve({
        type: 'batchDatasets',
        payload: { pid, ids: fetchIds, ck },
      })
      return [...fixedCache, ...(remoteDatasets || [])]
    }),
    batchDatasets: createEffect<{ pid: number; ids: number[]; ck?: boolean }>(function* ({ payload }, { call, put }) {
      const { pid, ids, ck } = payload
      if (!ids?.length) {
        return []
      }
      const { code, result } = yield call(batchDatasets, pid, ids, ck)
      if (code === 0) {
        const datasets = (result as YModels.BackendData[]).map(transferDataset)
        yield put({
          type: 'updateLocalDatasets',
          payload: datasets,
        })
        return datasets || []
      }
    }),
    batch: createEffect(function* ({ payload: ids }, { put }) {
      return yield put.resolve({
        type: 'batchLocalDatasets',
        payload: { ids },
      })
    }),
    getDataset: createEffect<{ id: number; verbose?: boolean; force?: boolean }>(function* ({ payload }, { call, put, select }) {
      const { id, verbose, force } = payload
      if (!force) {
        const dataset = yield select((state) => state.dataset.dataset[id])
        if (dataset) {
          return dataset
        }
      }
      const { code, result } = yield call(getDataset, id, verbose)
      if (code === 0) {
        const dataset = transferDataset(result)

        if (dataset.projectId) {
          const presult = yield put.resolve({
            type: 'project/getProject',
            payload: { id: dataset.projectId },
          })
          if (presult) {
            dataset.project = presult
          }
        }
        yield put({
          type: 'UpdateDataset',
          payload: { [id]: dataset },
        })
        return dataset
      }
    }),
    getDatasetVersions: createEffect<{ gid: number; force?: boolean }>(function* ({ payload }, { select, call, put }) {
      const { gid, force } = payload
      if (!force) {
        const versions = yield select(({ dataset }) => dataset.versions)
        if (versions[gid]) {
          return versions[gid]
        }
      }
      const { code, result } = yield call(getDatasetByGroup, gid)
      if (code === 0) {
        const vss = (result as List<YModels.BackendData>).items.map((item) => transferDataset(item))
        yield put({
          type: 'UpdateVersions',
          payload: {
            [gid]: vss,
          },
        })
        return vss
      }
    }),
    queryDatasets: createEffect<YParams.DatasetQuery>(function* ({ payload }, { select, call, put }) {
      const { code, result } = yield call(queryDatasets, payload)
      if (code === 0) {
        return { items: (result as List<YModels.BackendData>).items.map((ds) => transferDataset(ds)), total: result.total }
      }
    }),
    getHiddenList: createEffect<Omit<YParams.DatasetQuery, 'excludeType' | 'visible'>>(function* ({ payload }, { put }) {
      const query = { order_by: 'update_datetime', ...payload, excludeType: TASKTYPES.INFERENCE, visible: false }
      return yield put({
        type: 'queryDatasets',
        payload: query,
      })
    }),
    queryAllDatasets: createEffect<{ pid: number; force?: boolean }>(function* ({ payload }, { select, call, put }) {
      const loading = yield select(({ loading }) => {
        return loading.effects['dataset/queryDatasets']
      })
      const { pid, force } = payload
      if (!force) {
        const dssCache: YModels.Dataset[] = yield select((state) => state.dataset.allDatasets[pid])
        if (dssCache.length) {
          return dssCache
        }
      }
      if (loading) {
        return
      }
      const dss = yield put.resolve({ type: 'queryDatasets', payload: { pid, state: ResultStates.VALID, limit: 10000 } })
      if (dss) {
        yield put({
          type: 'UPDATE_ALL_DATASETS',
          payload: { [pid]: dss.items },
        })
        return dss.items
      }
    }),
    delDataset: createEffect<number>(function* ({ payload }, { call, put }) {
      const { code, result } = yield call(delDataset, payload)
      if (code === 0) {
        yield put({
          type: 'UpdateDataset',
          payload: { [payload]: null },
        })
        return result
      }
    }),
    delDatasetGroup: createEffect<number>(function* ({ payload }, { call, put }) {
      const { code, result } = yield call(delDatasetGroup, payload)
      if (code === 0) {
        return result
      }
    }),
    hide: createEffect<{ pid: number; ids: number[] }>(function* ({ payload: { pid, ids } }, { call, put }) {
      const { code, result } = yield call(batchAct, actions.hide, pid, ids)
      if (code === 0) {
        yield put({
          type: 'project/getProject',
          payload: {
            id: pid,
            force: true,
          },
        })
        return result.map(transferDataset)
      }
    }),
    restore: createEffect<{ pid: number; ids: number[] }>(function* ({ payload: { pid, ids } }, { call, put }) {
      const { code, result } = yield call(batchAct, actions.restore, pid, ids)
      if (code === 0) {
        yield put({
          type: 'project/getProject',
          payload: {
            id: pid,
            force: true,
          },
        })
        yield put.resolve({ type: 'clearCache' })
        return result
      }
    }),
    createDataset: createEffect<YParams.DatasetCreateParams>(function* ({ payload }, { call, put }) {
      const { code, result } = yield call(createDataset, payload)
      if (code === 0) {
        // yield put.resolve({ type: 'clearCache' })
        return result
      }
    }),
    updateDataset: createEffect<{ id: number; name: string }>(function* ({ payload }, { call, put }) {
      const { id, name } = payload
      const { code, result } = yield call(updateDataset, id, name)
      if (code === 0) {
        return result
      }
    }),
    getValidDatasetsCount: createEffect<number>(function* ({ payload: pid }, { call, put }) {
      const result = yield put.resolve({
        type: 'queryDatasets',
        payload: {
          pid,
          state: ResultStates.VALID,
          empty: false,
        },
      })
      if (result?.total) {
        yield put({
          type: 'UpdateValidDatasetCount',
          payload: result.total,
        })
        return result.total
      }
    }),
    getTrainingDatasetCount: createEffect<number>(function* ({ payload: pid }, { put }) {
      const result = yield put.resolve({
        type: 'queryDatasets',
        payload: {
          pid,
          state: ResultStates.VALID,
          haveClasses: true,
        },
      })

      if (result?.total) {
        yield put({
          type: 'UpdateTrainingDatasetCount',
          payload: result.total,
        })
        return result.total
      }
    }),
    updateVersion: createEffect<{ id: number; description: string }>(function* ({ payload }, { call, put }) {
      const { id, description } = payload
      const { code, result } = yield call(updateVersion, id, description)
      if (code === 0) {
        return transferDataset(result)
      }
    }),
    getInternalDataset: createEffect(function* ({ payload }, { call, put }) {
      const { code, result } = yield call(getInternalDataset, payload)
      if (code === 0) {
        const dss = (result as List<YModels.BackendData>).items.map((item) => transferDataset(item))
        const ds = { items: dss, total: result.total }
        yield put({
          type: 'UpdatePublicDatasets',
          payload: ds,
        })
        return ds
      }
    }),
    updateDatasets: createEffect<{ [key: string]: YModels.ProgressTask }>(function* ({ payload }, { put, select }) {
      const versions: DatasetState['versions'] = yield select((state) => state.dataset.versions)
      const tasks = payload || {}
      Object.keys(versions).forEach((gid) => {
        const datasets = versions[gid]
        let updatedDatasets = datasets.map((dataset) => {
          const updatedDataset = updateResultState(dataset, tasks)
          return updatedDataset ? { ...updatedDataset } : dataset
        })
        versions[gid] = updatedDatasets
      })
      yield put({
        type: 'UpdateVersions',
        payload: { ...versions },
      })
      return { ...versions }
    }),
    updateAllDatasets: createEffect<YModels.ProgressTask[]>(function* ({ payload: tasks = {} }, { put, select }) {
      const newDatasets = Object.values(tasks)
        .filter((task) => task.result_state === ResultStates.VALID)
        .map((task) => ({ id: task?.result_dataset?.id, needReload: true }))
      const pid = yield select(({ project }) => project.current?.id)
      if (newDatasets.length) {
        yield put({
          type: 'queryAllDatasets',
          payload: { pid, force: true },
        })
      }
    }),
    updateDatasetState: createEffect<{ [key: string]: YModels.ProgressTask }>(function* ({ payload }, { put, select }) {
      const caches = yield select((state) => state.dataset.dataset)
      const tasks = Object.values(payload || {})
      for (let index = 0; index < tasks.length; index++) {
        const task = tasks[index]
        const dataset = task?.result_dataset?.id ? caches[task?.result_dataset?.id] : undefined
        if (!dataset) {
          continue
        }
        const updated = updateResultByTask(dataset, task)
        if (updated?.id) {
          if (updated.needReload) {
            yield put({
              type: 'getDataset',
              payload: { id: updated.id, force: true },
            })
          } else {
            yield put({
              type: 'UpdateDataset',
              payload: { id: updated.id, dataset: { ...updated } },
            })
          }
        }
      }
    }),
    updateQuery: createEffect<YParams.DatasetsQuery>(function* ({ payload = {} }, { put, select }) {
      yield put({
        type: 'UpdateQuery',
        payload,
      })
    }),
    resetQuery: createEffect(function* ({}, { put }) {
      yield put({
        type: 'UpdateQuery',
        payload: initQuery,
      })
    }),
    clearCache: createEffect(function* ({}, { put }) {
      yield put({ type: 'CLEAR_ALL' })
    }),
    analysis: createEffect<{ pid: number; datasets: number[] }>(function* ({ payload }, { call, put }) {
      const { pid, datasets } = payload
      const { code, result } = yield call(analysis, pid, datasets)
      if (code === 0) {
        return result.map((item: YModels.BackendData) => transferDatasetAnalysis(item))
      }
    }),
    checkDuplication: createEffect<{ trainSet: number; validationSet: number }>(function* ({ payload }, { call, put, select }) {
      const { trainSet, validationSet } = payload
      const pid = yield select(({ project }) => project.current?.id)
      const { code, result } = yield call(checkDuplication, pid, trainSet, validationSet)
      if (code === 0) {
        return result
      }
    }),
    update: createEffect<YModels.BackendData>(function* ({ payload }, { put, select }) {
      const ds = transferDataset(payload)
      if (!ds.id) {
        return
      }
      const { versions } = yield select(({ dataset }) => dataset)
      // update versions
      const target = versions[ds.groupId] || []
      yield put({
        type: 'UpdateVersions',
        payload: {
          [ds.groupId]: [ds, ...target],
        },
      })
      // update dataset
      yield put({
        type: 'UpdateDataset',
        payload: {
          id: ds.id,
          dataset: ds,
        },
      })
    }),
    getNegativeKeywords: createEffect<YParams.DatasetQuery>(function* ({ payload }, { put, call, select }) {
      const { code, result } = yield call(getNegativeKeywords, { ...payload })
      if (code === 0) {
        const dataset = transferDataset(result)
        return dataset.gt
      }
    }),
    getCK: createEffect<{ ids?: number[]; pid: number }>(function* ({ payload }, { select, put }) {
      const { ids = [], pid } = payload
      const datasets = yield put.resolve({ type: 'batchDatasets', payload: { pid, ids, ck: true } })
      return datasets || []
    }),
    updateLocalDatasets: createEffect<YModels.Dataset[]>(function* ({ payload: datasets }, { put }) {
      for (let i = 0; i < datasets.length; i++) {
        const dataset = datasets[i]
        if (dataset?.id) {
          yield put({
            type: 'UpdateDataset',
            payload: { id: dataset.id, dataset },
          })
        }
      }
    }),
    getLocalDatasets: createEffect<number[] | undefined>(function* ({ payload: ids = [] }, { put, select }) {
      const datasets = yield select(({ dataset }) => dataset.dataset)
      return ids.map((id) => datasets[id]).filter((d) => d)
    }),
  },
  reducers: {
    ...reducers,
    CLEAR_ALL() {
      return deepClone(initState)
    },
  },
}

export default DatasetModal
