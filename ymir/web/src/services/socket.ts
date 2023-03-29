import { io, Socket } from 'socket.io-client'

let socket: Socket
export function getSocket(id: string) {
  const url = '/' + id

  if (!socket) {
    socket = io(url, {
      path: '/socket/ws/socket.io',
    })
    socket.off()
  }
  return socket
}
