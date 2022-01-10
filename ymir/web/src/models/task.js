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
    }
  },
  reducers: {
    updateTasks(state, { payload }) {
      const tasks = state.tasks.items
      const progressObj = {}
      payload.forEach(item => {
        progressObj[item.id] = item.progress
      });
      const result = tasks.map(task => progressObj[task.id] && (task.progress = progressObj[task.id]))
      console.log('update tasks: ', result, progressObj, payload)
      return {
        ...state,
        tasks: result,
      }
    },
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
      return history.listen(location => {
        console.log('get location: ', location)
        if (location.pathname === '/home/task') {
          socket = io('ws://localhost:8080/')
          // listen
          socket.on('connect', () => {
            console.log('socket connect.')
          })
          socket.on('updateTaskList', (data) => {
            console.log('updateTaskList data: ', data)
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
