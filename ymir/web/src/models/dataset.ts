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
  checkDuplicateNames,
} from '@/services/dataset'
import { transferDatasetGroup, transferDataset, transferDatasetAnalysis, transferAnnotationsCount, IMPORTSTRATEGY } from '@/constants/dataset'
import { actions, updateResultState, updateResultByTask, ResultStates, ImportingMaxCount } from '@/constants/common'
import { createEffect, createReducersByState } from './_utils'
import { deepClone } from '@/utils/object'
import { TASKTYPES } from '@/constants/task'
import { DatasetState, DatasetStore } from '.'
import { IdMap, List } from './typings/common.d'
import { Backend, Dataset, ImportingItem, ProgressTask } from '@/constants'
import { randomNumber } from '@/utils/number'
import { Types } from '@/components/dataset/add/AddTypes'
import { batchAdd } from '@/services/task'
import { message } from 'antd'

const initQuery = { name: '', type: '', time: 0, current: 1, offset: 0, limit: 20 }

const initState: DatasetState = {
  query: { ...initQuery },
  datasets: {},
  versions: {},
  dataset: {},
  allDatasets: {},
  publicDatasets: [],
  validDatasetCount: 0,
  trainingDatasetCount: 0,
  importing: {
    items: [],
    max: ImportingMaxCount,
  },
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
        const groups = (result as List<Backend>).items.map(transferDatasetGroup)
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
      const cache: Dataset[] = yield put.resolve({
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
        const datasets = (result as Backend[]).map(transferDataset)
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
        const vss = (result as List<Backend>).items.map((item) => transferDataset(item))
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
        return { items: (result as List<Backend>).items.map((ds) => transferDataset(ds)), total: result.total }
      }
    }),
    getHiddenList: createEffect<Omit<YParams.DatasetQuery, 'excludeType' | 'visible'>>(function* ({ payload }, { put }) {
      const query = { order_by: 'update_datetime', ...payload, excludeType: TASKTYPES.SYS, visible: false }
      return yield put({
        type: 'queryDatasets',
        payload: query,
      })
    }),
    queryAllDatasets: createEffect<{ pid: number; force?: boolean }>(function* ({ payload }, { select, call, put }) {
      const { pid, force } = payload
      if (!force) {
        const dssCache: Dataset[] = yield select((state) => state.dataset.allDatasets[pid])
        if (dssCache.length) {
          return dssCache
        }
      }
      const dss = yield put.resolve({ type: 'queryDatasets', payload: { pid, state: ResultStates.VALID, limit: 10000 } })
      if (dss) {
        yield put({
          type: 'UpdateAllDatasets',
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
        yield put({ type: 'keyword/UpdateReload', payload: true })
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

      if (result) {
        yield put({
          type: 'UpdateTrainingDatasetCount',
          payload: result?.total || 0,
        })
        return result.total
      }
    }),
    updateVersion: createEffect<{ id: number; description: string }>(function* ({ payload }, { call, put, select }) {
      const { id, description } = payload
      const { code, result } = yield call(updateVersion, id, description)
      if (code === 0) {
        const dataset = transferDataset(result)
        const versions: IdMap<Dataset[]> = yield select(({ dataset }) => dataset.versions)
        const groupVersions = versions[dataset.groupId] || []
        groupVersions.splice(
          groupVersions.findIndex((v) => v.id === dataset.id),
          1,
          dataset,
        )
        yield put({
          type: 'UpdateVersions',
          payload: {
            ...versions,
            [dataset.groupId]: [...groupVersions],
          },
        })
        return dataset
      }
    }),
    getInternalDataset: createEffect(function* ({ payload }, { call, put }) {
      const { code, result } = yield call(getInternalDataset, payload)
      if (code === 0) {
        const dss = (result as List<Backend>).items.map((item) => transferDataset(item))
        const ds = dss
        yield put({
          type: 'UpdatePublicDatasets',
          payload: dss,
        })
        return dss
      }
    }),
    updateDatasets: createEffect<{ [key: string]: ProgressTask }>(function* ({ payload }, { put, select }) {
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
    updateAllDatasets: createEffect<ProgressTask[]>(function* ({ payload: tasks = {} }, { put, select }) {
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
    updateDatasetState: createEffect<{ [key: string]: ProgressTask }>(function* ({ payload }, { put, select }) {
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
              payload: { [updated.id]: { ...updated } },
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
        return result.map((item: Backend) => transferDatasetAnalysis(item))
      }
    }),
    checkDuplication: createEffect<{ trainSet: number; validationSet: number }>(function* ({ payload }, { call, put, select }) {
      const { trainSet, validationSet } = payload
      const pid: number = yield select(({ project }) => project.current?.id)
      const { code, result } = yield call(checkDuplication, pid, trainSet, validationSet)
      if (code === 0) {
        return result
      }
    }),
    update: createEffect<Backend>(function* ({ payload }, { put, select }) {
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
          [ds.id]: ds,
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
    updateLocalDatasets: createEffect<Dataset[]>(function* ({ payload: datasets }, { put }) {
      for (let i = 0; i < datasets.length; i++) {
        const dataset = datasets[i]
        if (dataset?.id) {
          yield put({
            type: 'UpdateDataset',
            payload: { [dataset.id]: dataset },
          })
        }
      }
    }),
    getLocalDatasets: createEffect<number[] | undefined>(function* ({ payload: ids = [] }, { put, select }) {
      const datasets = yield select(({ dataset }) => dataset.dataset)
      return ids.map((id) => datasets[id]).filter((d) => d)
    }),
    addImportingList: createEffect<ImportingItem[]>(function* ({ payload: newItems }, { put, select }) {
      const { items }: DatasetState['importing'] = yield select(({ dataset }) => dataset.importing)
      const checkDuplicateName = (newName: string, list: ImportingItem[], index: number) => list.slice(0, index).find(({ name }) => name === newName)
      const updatedList = [...items, ...newItems]
      const list = updatedList.map((item, index) =>
        checkDuplicateName(item.name, updatedList, index) ? { ...item, name: item.name + '_' + randomNumber(3) } : item,
      )
      yield put({ type: 'updateImportingList', payload: list })
    }),
    removeImporting: createEffect<number[]>(function* ({ payload: indexs }, { put, select }) {
      const { items }: DatasetState['importing'] = yield select(({ dataset }) => dataset.importing)
      const updatedList = items.filter((item, index) => !indexs.includes(index))
      yield put({ type: 'updateImportingList', payload: updatedList })
    }),
    updateImportingItem: createEffect<ImportingItem>(function* ({ payload: item }, { put, select }) {
      const { items }: DatasetState['importing'] = yield select(({ dataset }) => dataset.importing)
      const updatedList = items.map((old) => (old.index === item.index ? item : old))
      yield put({ type: 'updateImportingList', payload: updatedList })
    }),
    updateImportingList: createEffect<ImportingItem[]>(function* ({ payload: items }, { put }) {
      const updatedMax = ImportingMaxCount - items.length
      const uniqueItems = items.reduce<ImportingItem[]>((prev, curr) => {
        return prev.some((item) => item.source === curr.source) ? prev : [...prev, curr]
      }, [])
      yield put({
        type: 'UpdateImporting',
        payload: {
          items: uniqueItems.map((item, index) => {
            const source = typeof item.source === 'string' ? item.source.trim() : item.source
            return { ...item, source, name: item.name.trim(), index }
          }),
          max: updatedMax,
        },
      })
    }),
    clearImporting: createEffect(function* ({}, { put }) {
      yield put({ type: 'UpdateImporting', payload: { items: [], max: ImportingMaxCount, editing: false } })
    }),
    showFormatDetail: createEffect<boolean>(function* ({ payload: visible }, { put, select }) {
      yield put({ type: 'UpdateImporting', payload: { formatVisible: visible } })
    }),
    updateImportingEditState: createEffect<boolean>(function* ({ payload: editing }, { put }) {
      yield put({
        type: 'UpdateImporting',
        payload: {
          editing,
        },
      })
    }),
    checkDuplicateNames: createEffect<{ pid: number; names: string[] }>(function* ({ payload: { pid, names } }, { put, call }) {
      const { code, result } = yield call(checkDuplicateNames, pid, names)
      if (code === 0) {
        return result?.names || []
      }
    }),
    batchAdd: createEffect<{ pid: number }>(function* ({ payload: { pid } }, { call, put, select }) {
      const items: ImportingItem[] = yield select(({ dataset }) => dataset.importing.items)
      if (items.length !== [...new Set(items.map((item) => item.name))].length) {
        return message.error('duplicated name')
      }
      const duplicateChecked: string[] = yield put.resolve({
        type: 'checkDuplicateNames',
        payload: { pid, names: items.map((item) => item.name) },
      })
      if (duplicateChecked.length) {
        yield put({
          type: 'updateImportingList',
          payload: items.map((item) => (duplicateChecked.includes(item.name) ? { ...item, dup: true } : item)),
        })
        return
      }
      const params = items.map((item) => {
        const field = {
          [Types.LOCAL]: 'url',
          [Types.NET]: 'url',
          [Types.COPY]: 'dataset_id',
          [Types.INTERNAL]: 'dataset_id',
          [Types.PATH]: 'path',
        }[item.type]
        return {
          dataset_group_name: item.name,
          [field]: item.source,
          strategy: item.strategy || IMPORTSTRATEGY.UNKOWN_KEYWORDS_AUTO_ADD,
        }
      })
      const newClasses = [...new Set(items.reduce<string[]>((prev, { classes = [] }) => [...prev, ...classes], []))]
      if (newClasses.length) {
        yield put.resolve({
          type: 'keyword/updateKeywords',
          payload: { keywords: newClasses.map((cls) => ({ name: cls })) },
        })
      }
      const { code, result } = yield call(batchAdd, pid, params)
      if (code === 0) {
        yield put.resolve({
          type: 'clearImporting',
        })
        return result
      }
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
