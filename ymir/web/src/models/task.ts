import { stopTask, fusion, merge, filter, mine, train, label, infer, batchAdd } from '@/services/task'
import { createEffect, createReducersByState } from './_utils'
import { MergeParams } from '@/services/task.d'
import { TaskState, TaskStore } from '.'
import { ImportingItem } from '@/constants'
import { Types } from '@/components/dataset/add/AddTypes'

const state: TaskState = {}

const TaskModel: TaskStore = {
  namespace: 'task',
  state,
  effects: {
    stopTask: createEffect<{ id: number; with_data?: boolean }>(function* ({ payload }, { call, put }) {
      const { id, with_data } = payload
      let { code, result } = yield call(stopTask, id, with_data)
      if (code === 0) {
        yield put.resolve({
          type: 'dataset/clearCache',
        })
        yield put.resolve({
          type: 'model/clearCache',
        })
        return result
      }
    }),
    fusion: createEffect(function* ({ payload }, { call, put }) {
      let { code, result } = yield call(fusion, payload)
      if (code === 0) {
        if (result?.result_dataset?.id) {
          yield put.resolve({
            type: 'dataset/getDataset',
            payload: { id: result?.result_dataset?.id },
          })
        }
        return result
      }
    }),
    merge: createEffect<MergeParams>(function* ({ payload }, { call, put }) {
      let { code, result } = yield call(merge, payload)
      if (code === 0) {
        if (result?.result_dataset?.id) {
          yield put.resolve({
            type: 'dataset/getDataset',
            payload: { id: result?.result_dataset?.id },
          })
        }
        return result
      }
    }),
    filter: createEffect(function* ({ payload }, { call, put }) {
      let { code, result } = yield call(filter, payload)
      if (code === 0) {
        if (result?.result_dataset?.id) {
          yield put.resolve({
            type: 'dataset/getDataset',
            payload: { id: result?.result_dataset?.id },
          })
        }
        return result
      }
    }),
    train: createEffect(function* ({ payload }, { call, put }) {
      let { code, result } = yield call(train, payload)
      if (code === 0) {
        yield put({
          type: 'model/getModel',
          payload: { id: result?.result_model?.id, force: true },
        })
        return result
      }
    }),
    mine: createEffect(function* ({ payload }, { call, put }) {
      let { code, result } = yield call(mine, payload)
      if (code === 0) {
        yield put({
          type: 'dataset/getDataset',
          payload: { id: result?.result_dataset?.id, force: true },
        })
        return result
      }
    }),
    label: createEffect<{ keywords: string[] }>(function* ({ payload }, { call, put }) {
      const { keywords } = payload
      yield put.resolve({
        type: 'keyword/updateKeywords',
        payload: { keywords: keywords.map((kw) => ({ name: kw, aliases: [] })) },
      })
      let { code, result } = yield call(label, payload)
      if (code === 0) {
        yield put({
          type: 'dataset/getDataset',
          payload: { id: result?.result_dataset?.id, force: true },
        })
        return result
      }
    }),
    infer: createEffect(function* ({ payload }, { call, put }) {
      let { code, result } = yield call(infer, payload)
      if (code === 0) {
        const id = result?.result_dataset?.id
        const pid = result?.project_id
        if (pid && id) {
          yield put({
            type: 'dataset/batchLocalDatasets',
            payload: { ids: [id], pid },
          })
        }
        return result
      }
    }),
    batchAdd: createEffect<{ pid: number }>(function* ({ payload: { pid } }, { call, put, select }) {
      const items: ImportingItem[] = yield select(({ dataset }) => dataset.importing.items)
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
        }
      })
      const { code, result } = yield call(batchAdd, pid, params)
      if (code === 0) {
        yield put({
          type: 'dataset/UpdateImportingList',
          payload: {
            items: [],
          },
        })
        return result
      }
    }),
  },
  reducers: createReducersByState(state),
}

export default TaskModel
