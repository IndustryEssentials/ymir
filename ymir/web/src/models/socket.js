import { getSocket } from '../services/socket'

const pageMaps = [
  { path: '/home/task', method: 'task/updateTasks' },
  { path: '/home/dataset', method: 'dataset/updateDatasets' },
]

export default {
  state: {},
  namespace: "socket",
  subscriptions: {
    setup({ dispatch, history }) {
        let socket = null
      return history.listen(async location => {
        if (pageMaps.some(page => page.path === location.pathname)) {
          const { id } = await dispatch({
            type: 'user/getUserInfo',
          })
          socket = getSocket(id)

          socket.on('update_taskstate', (data) => {
            pageMaps.forEach(page => dispatch({
              type: page.method,
              payload: data,
            }))
          })
        } else {
          // other page close socket
          socket && socket.close()
        }
      })
    },
  }
}
