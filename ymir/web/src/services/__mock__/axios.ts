const mockAxios: any = jest.genMockFromModule("axios")

// this is the key to fix the axios.create() undefined error!
mockAxios.create = jest.fn(() => mockAxios)
mockAxios.get = jest.fn(() => Promise.resolve({ data: {} }))
mockAxios.post = jest.fn(() => Promise.resolve({ data: {} }))
mockAxios.put = jest.fn(() => Promise.resolve({ data: {} }))
mockAxios.delete = jest.fn(() => Promise.resolve({ data: {} }))
mockAxios.all = jest.fn(() => Promise.resolve())

mockAxios.interceptors = {
  request: { use: jest.fn() },
  response: { use: jest.fn() },
}

export default mockAxios
