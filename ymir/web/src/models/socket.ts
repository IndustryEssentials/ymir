import { getSocket } from '../services/socket'
import { readyState } from '@/constants/common'
import { createEffect } from './_utils'
import { history } from 'umi'
import { Socket as SocketType } from 'socket.io-client'
import { SocketStore } from '.'
import { IdMap } from './typings/common.d'
import { Backend, Image, ProgressTask, User } from '@/constants'
import image from '@/locales/modules/image'
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
      const { hash } = yield put.resolve<null, User>({
        type: 'user/getUserInfo',
      })
      socket = getSocket(hash)
      yield put({
        type: 'updateSocket',
        payload: socket,
      })
      return socket
    }),
    saveUpdatedTasks: createEffect<IdMap<ProgressTask>>(function* ({ payload = {} }, { put }) {
      const tasks = Object.keys(payload).map((hash) => ({
        ...payload[hash],
        hash,
        reload: !readyState(payload[hash].result_state),
      }))
      yield put({ type: 'saveTasks', payload: tasks })
    }),
    asyncMessages: createEffect<Backend[]>(function* ({ payload }, { put }) {
      yield put({
        type: 'message/asyncMessages',
        payload,
      })
    }),
    updateGroundedSamImage: createEffect<ProgressTask[]>(function* ({ payload: tasks }, { put, select }) {
      const gsImage: Image | undefined = yield select(({ image }) => image.groundedSAM)
      const imageTask = tasks.find(({ result_image }) => result_image?.id)
      if (gsImage && imageTask && gsImage?.id === imageTask?.result_image?.id) {
        const image = { ...gsImage, state: imageTask.result_state }
        yield put({
          type: 'image/UpdateGroundedSAM',
          payload: image,
        })
      }
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

            const tasks: ProgressTask[] = Object.keys(data).map((hash) => ({
              ...data[hash],
              hash,
              reload: !readyState(data[hash].result_state),
            }))
            // cache socket valid data
            dispatch({ type: 'saveUpdatedTasks', payload: data })
            // update data in socket model by dispatch effects
            dispatch({ type: 'updateGroundedSamImage', payload: tasks })
          })
          .on('update_message', (data) => {
            dispatch({ type: 'asyncMessages', payload: data })
          })
      })
    },
  },
}

export default Socket
