import request from '@/utils/request'

jest.mock('@/utils/request', () => {
  const req = jest.fn()
  req.get = jest.fn()
  req.post = jest.fn()
  return req
})

console.error = jest.fn()
export const product = (id) => ({ id })

export const products = (n) => Array.from({ length: n }, (item, index) => product(index + 1))

const response = (result, code = 0) => ({ code, result })

const getRequestResponseOnce = (result, method = '', code = 0) =>
  (method ? request[method]: request).mockImplementationOnce(() => Promise.resolve(response(result, code))).mockRejectedValue(new Error('rejected!'))


export const requestExample = (func, params, expected, method = '', cd = 0) => {
  getRequestResponseOnce(expected, method, cd)
  const promise = Array.isArray(params) ? func(...params) : func(params)
  promise.then(({ code, result }) => {
    expect(code).toBe(cd)
    expect(result).toEqual(expected)
  }).catch(err => console.error(err))
}