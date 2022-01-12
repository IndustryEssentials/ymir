import { io } from 'socket.io-client'
import {
  getTasks,
  getTask,
  deleteTask,
  updateTask,
  createTask,
  stopTask,
  getLabelData,
  createFilterTask,
  createMiningTask,
  createTrainTask,
  createLabelTask,
} from "@/services/task"
import { getSocket } from '../services/socket'

export default {
  namespace: "task",
  state: {
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
          const datasets = yield put.resolve({ type: 'dataset/batchDatasets', payload: ids })
          const findDs = (dss) => dss.map(sid => datasets.find(ds => ds.id === sid))
          if (datasets && datasets.length) {
            result['filterSets'] = findDs(filterSets)
            result['trainSets'] = findDs(trainSets)
            result['testSets'] = findDs(testSets)
            result['excludeSets'] = findDs(excludeSets)
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
        yield put({
          type: "UPDATE_TASKS",
          payload: result,
        })
        return result
      }
    },
    *stopTask({ payload }, { call, put }) {
      console.log('task model stop task', payload)
      const { id, with_data } = payload
      let { code, result } = yield call(stopTask, id, with_data)
      if (code === 0) {
        return result
      }
    },
    *getLabelData({ payload }, { call, put }) {
      let { code, result } = yield call(getLabelData, payload)
      if (code === 0) {
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
    // *createTask({ payload }, { call, put }) {
    //   let { code, result } = yield call(createTask, payload)
    //   if (code === 0) {
    //     return result
    //   }
    //   return {
    //     code,
    //   }
    // },
    *createFilterTask({ payload }, { call, put }) {
      let { code, result } = yield call(createFilterTask, payload)
      if (code === 0) {
        return result
      }
    },
    *createTrainTask({ payload }, { call, put }) {
      let { code, result } = yield call(createTrainTask, payload)
      if (code === 0) {
        return result
      }
    },
    *createMiningTask({ payload }, { call, put }) {
      let { code, result } = yield call(createMiningTask, payload)
      if (code === 0) {
        return result
      }
    },
    *createLabelTask({ payload }, { call, put }) {
      let { code, result } = yield call(createLabelTask, payload)
      if (code === 0) {
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
        }
        return task
      })
      yield put({
        type: 'UPDATE_TASKS',
        payload: { items: result, total: tasks.total },
      })
    },
    *getUsername({ payload }, { select }) {
      const username = yield select(({ user }) => user.username)
      if (username) {
        return username
      }
    }
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
  },
  subscriptions: {
    setup({ dispatch, history }) {
        let socket = null
      return history.listen(async location => {
        if (location.pathname === '/home/task') {
          const { id } = await dispatch({
            type: 'user/getUserInfo',
          })
          socket = getSocket(id)

          socket.on('update_taskstate', (data) => {
            console.log(data)
            dispatch({
              type: 'updateTasks',
              payload: data,
            })
          })
        } else {
          // other page close socket
          socket && socket.close()
        }
      })
    },
  }
}
