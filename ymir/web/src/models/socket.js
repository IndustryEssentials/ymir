import { getSocket } from '../services/socket'

const pageMaps = [
  { path: '/home/project/detail/\\d+', method: 'dataset/updateDatasets' },
  { path: '/home/project/detail/\\d+', method: 'dataset/updateDatasetState' },
  { path: '/home/project/detail/\\d+', method: 'model/updateModelState' },
  { path: '/home/project/detail/\\d+', method: 'iteration/updateCurrentStageResult' },
  { path: '/home/project/detail/\\d+', method: 'model/updateModelsStates' },
  { path: '/home/project/\\d+/model/\\d+', method: 'model/updateModelState' },
  { path: '/home/project/\\d+/dataset/\\d+', method: 'dataset/updateDatasetState' },
]

export default {
  state: {
    socket: null,
  },
  namespace: "socket",
  effects: {
    *getSocket({ payload }, { put, select }) {
      let socket = yield select(state => state.socket.socket)
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
    }
  },
  reducers: {
    updateSocket(state, { payload }) {
      return {
        ...state,
        socket: payload,
      }
    }
  },
  subscriptions: {
    setup({ dispatch, history }) {
      return history.listen(async location => {
        if (pageMaps.some(page => new RegExp(`^${page.path}$`).test(location.pathname))) {
          let socket = await dispatch({
            type: 'getSocket',
          })
          socket.off().on('update_taskstate', (data) => {
            pageMaps.forEach(page => dispatch({
              type: page.method,
              payload: data,
            }))
          })
        }
      })
    },
  }
}
