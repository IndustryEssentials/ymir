import {
  getTasks,
  getTask,
  deleteTask,
  updateTask,
  stopTask,
  fusion,
  merge,
  filter,
  mine,
  train,
  label,
  infer,
} from "@/services/task"
import { TASKTYPES, TASKSTATES, isFinalState } from '@/constants/task'

const initQuery = {
  name: '',
  type: '',
  state: '',
  time: 0,
  offset: 0,
  limit: 20,
}

export default {
  namespace: "task",
  state: {
    query: initQuery,
    tasks: {
      items: [],
      total: 0,
    },
    task: {}
  },
  effects: {
    *getTasks({ payload }, { call, put }) {
      let { code, result } = yield call(getTasks, payload)
      if (code === 0) {
        yield put({
          type: "UPDATE_TASKS",
          payload: result,
        })
        return result
      }
    },
    *queryInferTasks({ payload }, { call, put }) {
      const params = { ...payload, type: TASKTYPES.INFERENCE, state: TASKSTATES.FINISH, limit: 1000 }
      const result = yield put.resolve({ type: 'getTasks', payload: params })
      if (result) {
        return result.items
      }
    },
    *getTask({ payload }, { call, put }) {
      let { code, result } = yield call(getTask, payload)
      if (code === 0) {
        const ps = result.parameters
        const filterSets = ps.include_datasets || []
        const trainSets = ps.include_train_datasets || []
        const testSets = ps.include_validation_datasets || []
        const excludeSets = ps.exclude_datasets || []
        const ids = [
          ...filterSets,
          ...trainSets,
          ...testSets,
          ...excludeSets,
        ]
        if (ids.length) {
          const datasets = yield put.resolve({ type: 'dataset/batchDatasets', payload: { pid: result?.project_id, ids } })
          const findDs = (dss) => dss.map(sid => datasets.find(ds => ds.id === sid))
          if (datasets && datasets.length) {
            result['filterSets'] = findDs(filterSets)
            result['trainSets'] = findDs(trainSets)
            result['testSets'] = findDs(testSets)
            result['excludeSets'] = findDs(excludeSets)
          }
          if (ps.model_id) {
            const model = yield put.resolve({ type: 'model/getModel', payload: ps.model_id })
            result['model'] = model
          }
          yield put({
            type: "UPDATE_TASK",
            payload: result,
          })
        }
        return result
      }
    },
    *deleteTask({ payload }, { call, put }) {
      let { code, result } = yield call(deleteTask, payload)
      if (code === 0) {
        return result
      }
    },
    *stopTask({ payload }, { call, put }) {
      const { id, with_data } = payload
      let { code, result } = yield call(stopTask, id, with_data)
      if (code === 0) {
        yield put.resolve({
          type: 'dataset/clearCache'
        })
        yield put.resolve({
          type: 'model/clearCache'
        })
        return result
      }
    },
    *updateTask({ payload }, { call, put }) {
      const { id, name } = payload
      let { code, result } = yield call(updateTask, id, name)
      if (code === 0) {
        yield put({
          type: "UPDATE_TASK",
          payload: result,
        })
        return result
      }
    },
    *fusion({ payload }, { call, put }) {
      let { code, result } = yield call(fusion, payload)
      if (code === 0) {
        yield put.resolve({
          type: 'dataset/update',
          payload: result,
        })
        return result
      }
    },
    *merge({ payload }, { call, put }) {
      let { code, result } = yield call(merge, payload)
      if (code === 0) {
        yield put.resolve({
          type: 'dataset/update',
          payload: result,
        })
        return result
      }
    },
    *filter({ payload }, { call, put }) {
      let { code, result } = yield call(filter, payload)
      if (code === 0) {
        yield put.resolve({
          type: 'dataset/update',
          payload: result,
        })
        return result
      }
    },
    *train({ payload }, { call, put }) {
      let { code, result } = yield call(train, payload)
      if (code === 0) {
        yield put({
          type: 'model/getModel',
          payload: { id: result?.result_model?.id, force: true }
        })
        return result
      }
    },
    *mine({ payload }, { call, put }) {
      let { code, result } = yield call(mine, payload)
      if (code === 0) {
        yield put({
          type: 'dataset/getDataset',
          payload: { id: result?.result_dataset?.id, force: true }
        })
        return result
      }
    },
    *label({ payload }, { call, put }) {
      let { code, result } = yield call(label, payload)
      if (code === 0) {
        yield put({
          type: 'dataset/getDataset',
          payload: { id: result?.result_dataset?.id, force: true }
        })
        return result
      }
    },
    *infer({ payload }, { call, put }) {
      let { code, result } = yield call(infer, payload)
      if (code === 0) {
        yield put({
          type: 'dataset/getDataset',
          payload: { id: result?.result_dataset?.id, force: true }
        })
        return result
      }
    },
    *updateTasks({ payload }, { put, select }) {
      const tasks = yield select(state => state.task.tasks)
      const updateList = payload || {}
      const result = tasks.items.map(task => {
        const updateItem = updateList[task.hash]
        if (updateItem) {
          task.state = updateItem.state
          task.progress = updateItem.percent * 100
          if (isFinalState(updateItem.state)) {
            task.forceUpdate = true
          }
        }
        return task
      })
      yield put({
        type: 'UPDATE_TASKS',
        payload: { items: result, total: tasks.total },
      })
    },
    *updateQuery({ payload = {} }, { put, select }) {
      const query = yield select(({ task }) => task.query)
      yield put({
        type: 'UPDATE_QUERY',
        payload: {
          ...query,
          ...payload,
          offset: query.offset === payload.offset ? initQuery.offset : payload.offset,
        }
      })
    },
    *resetQuery({ }, { put }) {
      yield put({
        type: 'UPDATE_QUERY',
        payload: initQuery,
      })
    },
  },
  reducers: {
    UPDATE_TASKS(state, { payload }) {
      return {
        ...state,
        tasks: payload,
      }
    },
    UPDATE_TASK(state, { payload }) {
      return {
        ...state,
        task: payload,
      }
    },
    UPDATE_QUERY(state, { payload }) {
      return {
        ...state,
        query: payload,
      }
    },
  },
}
