import {
  getSocket
} from "../socket"

jest.mock('socket.io-client', () => {
  const socket = {
    on: jest.fn(),
    off: jest.fn(),
  }
  const io = jest.fn(() => socket)
  return {
    io,
  }
})

describe("service: socket", () => {
  it('getSocket -> success', () => {
    const userHash = '0005'
    const socket = getSocket(userHash)
    expect(socket.off).toHaveBeenCalled()
    const socket2 = getSocket(userHash)
    expect(socket2).toBe(socket)
  })
})
