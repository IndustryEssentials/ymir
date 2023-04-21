import { getSocket } from '../services/socket'
import { readyState } from '@/constants/common'
import { createEffect } from './_utils'
import { history } from 'umi'
import { Socket as SocketType } from 'socket.io-client'
import { SocketStore } from '.'
import { IdMap } from './typings/common'
history
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
  { path: '/home/project/\\d+/prediction', method: 'dataset/updateDatasets' },
]

const Socket: SocketStore = {
  state: {
    socket: undefined,
    tasks: [],
  },
  namespace: 'socket',
  effects: {
    getSocket: createEffect(function* ({ payload }, { put, select }) {
      let socket = yield select((state) => state.socket.socket)
      if (socket) {
        return socket
      }
      const { hash } = yield put.resolve<null, YModels.User>({
        type: 'user/getUserInfo',
      })
      socket = getSocket(hash)
      yield put({
        type: 'updateSocket',
        payload: socket,
      })
      return socket
    }),
    saveUpdatedTasks: createEffect<IdMap<YModels.ProgressTask>>(function* ({ payload = {} }, { put }) {
      const tasks = Object.keys(payload).map((hash) => ({
        ...payload[hash],
        hash,
        reload: !readyState(payload[hash].result_state),
      }))
      yield put({ type: 'saveTasks', payload: tasks })
    }),
    asyncMessages: createEffect<YModels.BackendData[]>(function* ({ payload }, { put }) {
      yield put({
        type: 'message/asyncMessages',
        payload,
      })
    }),
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
        let socket = await dispatch<any, SocketType>({
          type: 'getSocket',
        })
        socket
          .off()
          .on('update_taskstate', (data) => {
            pageMaps.forEach((page) => dispatch({ type: page.method, payload: data }))
            // cache socket valid data
            dispatch({ type: 'saveUpdatedTasks', payload: data })
          })
          .on('update_message', (data) => {
            dispatch({ type: 'asyncMessages', payload: data })
          })
      })
    },
  },
}

export default Socket
