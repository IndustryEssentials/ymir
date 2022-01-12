import { io } from 'socket.io-client'

export function getSocket(id) {
  let socket = null
  const url = '/' + id

  if (!socket) {
    socket = io(url, {
      path: '/socket/ws/socket.io'
    })
    socket.off()
  }
  return socket
}

