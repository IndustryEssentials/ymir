import { history, getDvaApp } from 'umi'

const token = 'itistokenstring'

jest.mock('umi', () => {
  const dvaApp = {
    _store: {
      dispatch: jest.fn(),
    },
  }
  return {
    history: {
      push: jest.fn(),
      replace: jest.fn(),
      location: {
        pathname: 'testpathname',
      },
    },
    getDvaApp: jest.fn(() => dvaApp),
  }
})

jest.mock('@/utils/storage', () => {
  return {
    get: jest.fn(() => token),
    remove: jest.fn(),
  }
})

jest.mock('@/utils/t', () => jest.fn((msg) => msg))

jest.mock('@/hooks/useErrorMessage', () => () => jest.fn((code) => code))

const err = 'it is a test error message'

describe('utils: request', () => {
  let consoleSpy

  beforeEach(() => {
    process.env.APIURL = 'https://www.baidu.com/'
    process.env.NODE_ENV = ''
    consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('set the right base url', () => {
    jest.isolateModules(() => {
      const request = require('../request').default

      expect(request.defaults.baseURL).toBe(process.env.APIURL)
    })
  })
  it('get dev base url', () => {
    jest.isolateModules(() => {
      const expected = 'devurl'
      process.env.NODE_ENV = 'development'
      process.env.APIURL = expected
      const devReq = require('../request').default
      expect(devReq.defaults.baseURL).toBe(expected)
    })
  })
  it('get base url with window.baseConfig', () => {
    jest.isolateModules(() => {
      const expected = 'widnow.baseConfig.url'
      window.baseConfig = {
        APIURL: expected,
      }
      const devReq = require('../request').default
      expect(devReq.defaults.baseURL).toBe(expected)
    })
  })
  it('a request interceptor to the request', () => {
    const request = require('../request').default
    const config = { headers: { 'Content-Type': 'text/plain' } }
    const defaultConfig = { headers: {} }
    const reqHandler = request.interceptors.request.handlers[0]

    const defConfig = reqHandler.fulfilled(defaultConfig)

    const iconfig = reqHandler.fulfilled(config)

    // request resolve
    expect(defConfig.headers).toHaveProperty('Authorization', expect.stringContaining(token))
    expect(iconfig.headers).toHaveProperty('Authorization', expect.stringContaining(token))

    // request reject
    const errRes = reqHandler.rejected(err)
    expect(errRes).toBe(err)
  })

  it('a response interceptor to the request', () => {
    const request = require('../request').default
    const normal = (code = 0, result = null) => ({ status: 200, data: { code, result } })
    const error = (status, data = null) => ({ request: { status }, response: { data } })

    const res = normal(0, { access_token: token })
    const res110104 = normal(110104)
    const res10001 = normal(10001)

    const error400110104 = error(400, { code: 110104 })
    const error4001003 = error(400, { code: 1003 })
    const error401 = error(401)
    const error403 = error(403)
    const error405 = error(405)
    const error500 = error(500)
    const error502 = error(502)
    const error504 = error(504)

    const reqHandler = request.interceptors.response.handlers[0]

    // 200 -> normal
    const { code, result } = reqHandler.fulfilled(res)
    expect(code).toBe(0)
    expect(result.access_token).toBe(token)

    // 200 -> 110104
    const res110104Result = reqHandler.fulfilled(res110104)
    expect(getDvaApp).toHaveBeenCalled()
    expect(getDvaApp()._store.dispatch).toHaveBeenCalled()
    expect(res110104Result).toEqual(res110104.data)

    // 200 -> 10001
    const res10001Result = reqHandler.fulfilled(res10001)
    expect(res10001Result.code).toBe(10001)

    // 401

    const error401Result = reqHandler.rejected(error401)
    expect(getDvaApp()._store.dispatch).toHaveBeenCalled()
    expect(error401Result).toBeUndefined()

    // 403
    const error403Result = reqHandler.rejected(error403)
    expect(getDvaApp).toHaveBeenCalled()
    expect(getDvaApp()._store.dispatch).toHaveBeenCalled()
    expect(error403Result).toBeUndefined()

    // 400 -> 1003
    const error4001003Result = reqHandler.rejected(error4001003)
    expect(error4001003Result).toEqual({ code: 1003 })

    // 400 -> 110104
    const error400110104Result = reqHandler.rejected(error400110104)
    expect(getDvaApp).toHaveBeenCalled()
    expect(getDvaApp()._store.dispatch).toHaveBeenCalled()
    expect(error400110104Result).toBeUndefined()

    // 405
    const error405Result = reqHandler.rejected(error405)
    expect(error405Result).toEqual({ code: 405 })

    // 504
    const error504Result = reqHandler.rejected(error504)
    expect(error504Result).toEqual({ code: 504 })

    // 500
    const error500Result = reqHandler.rejected(error500)
    expect(error500Result).toEqual({ code: 500 })

    // 502
    const error502Result = reqHandler.rejected(error502)
    expect(error502Result).toEqual({ code: 502 })
  })
})
