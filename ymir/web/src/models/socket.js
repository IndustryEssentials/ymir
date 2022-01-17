import { getSocket } from '../services/socket'

const pageMaps = [
  { path: '/home/task', method: 'task/updateTasks' },
  { path: '/home/task/detail/\\d+', method: 'task/updateTaskState' },
  { path: '/home/dataset', method: 'dataset/updateDatasets' },
]

export default {
  state: {},
  namespace: "socket",
  subscriptions: {
    setup({ dispatch, history }) {
      let socket = null
      return history.listen(async location => {
        if (pageMaps.some(page => new RegExp(`^${page.path}$`).test(location.pathname))) {
          const { hash } = await dispatch({
            type: 'user/getUserInfo',
          })
          socket = getSocket(hash)

          socket.on('update_taskstate', (data) => {
            // console.log('socket -> update_taskstate data: ', data)
            setTimeout(() => pageMaps.forEach(page => dispatch({
              type: page.method,
              payload: data,
            })), 2000)
          })
        } else {
          // other page close socket
          socket && socket.close()
        }
      })
    },
  }
}
