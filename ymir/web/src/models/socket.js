import { getSocket } from '../services/socket'
import { validState } from '@/constants/common'

const pageMaps = [
  { path: '/home/project/\\d+/dataset', method: 'dataset/updateDatasets' },
  { path: '/home/project/\\d+/model', method: 'model/updateModelsStates' },
  { path: '/home/project/\\d+/model/\\d+', method: 'model/updateModelState' },
  { path: '/home/project/\\d+/dataset/\\d+', method: 'dataset/updateDatasetState' },
  { path: '/home/project/\\d+/iterations', method: 'dataset/updateAllDatasets' },
  { path: '/home/project/\\d+/iterations', method: 'dataset/updateDatasetState' },
  { path: '/home/project/\\d+/iterations', method: 'model/updateModelState' },
  { path: '/home/project/\\d+/iterations', method: 'project/updateProjectTrainSet' },
  { path: '/home/project/\\d+/iterations', method: 'iteration/updateIterationCache' },
  { path: '/home/project/\\d+/diagnose', method: 'dataset/updateDatasets' },
]

export default {
  state: {
    socket: null,
    tasks: [],
  },
  namespace: 'socket',
  effects: {
    *getSocket({ payload }, { put, select }) {
      let socket = yield select((state) => state.socket.socket)
      if (socket) {
        return socket
      }
      const { hash } = yield put.resolve({
        type: 'user/getUserInfo',
      })
      socket = getSocket(hash)
      yield put({
        type: 'updateSocket',
        payload: socket,
      })
      return socket
    },
    *saveUpdatedTasks({ payload }, { put }) {
      const tasks = Object.keys(payload).map((hash) => ({
        ...payload[hash],
        hash,
        reload: validState(payload[hash].result_state),
      }))
      yield put({ type: 'saveTasks', payload: tasks })
    },
  },
  reducers: {
    updateSocket(state, { payload }) {
      return { ...state, socket: payload }
    },
    saveTasks(state, { payload }) {
      return { ...state, tasks: payload }
    },
  },
  subscriptions: {
    setup({ dispatch, history }) {
      return history.listen(async (location) => {
        if (pageMaps.some((page) => new RegExp(`^${page.path}$`).test(location.pathname))) {
          let socket = await dispatch({
            type: 'getSocket',
          })
          socket.off().on('update_taskstate', (data) => {
            pageMaps.forEach((page) => dispatch({ type: page.method, payload: data }))
            // cache socket valid data
            dispatch({ type: 'saveUpdatedTasks', payload: data })
          })
        }
      })
    },
  },
}
