import request from '@/utils/request'

import {
  getUploadUrl,
  getTensorboardLink,
  getHistory,
  getStats,
} from '../common'

jest.mock('@/utils/request', () => {
  return {
    get: jest.fn(),
    post: jest.fn(),
  }
})

describe('service: common', () => {
  it('common:getUploadUrl', () => {
    process.env.APIURL = '/test/api/url'
    const path = 'uploadfile/'

    expect(getUploadUrl()).toBe(process.env.APIURL + path)

    window.baseConfig = { APIURL: 'test/from/base/config' }
    expect(getUploadUrl()).toBe(window.baseConfig.APIURL + path)
    
    process.env.NODE_ENV = 'development'
    expect(getUploadUrl()).toBe(process.env.APIURL + path)
  })
  it('common:getTensorboardLink', () => {
    const path = '/tensorboard/#scalars&regexInput='
    const hash = 't23412352134215312342'

    expect(getTensorboardLink(hash)).toBe(path + hash)
    expect(getTensorboardLink()).toBe(path)
    expect(getTensorboardLink(null)).toBe(path)
  })
  it('common:getHistory', () => {
    const params = {}
    const expected = {
      edges: [1,2,3,4],
      nodes: [5,6,7,8],
    }
    request.get.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: expected,
      })
    })

    getHistory(params).then(({ result }) => {
      expect(result).toEqual(expected)
    })
  })
  it('common:getStats', () => {
    const params1 = { q: 'ds', limit: 3 }
    const params2 = { q: 'mms', limit: 3 }
    const params3 = { q: 'hms', limit: 3 }
    const params4 = { q: 'hkw' }
    const params5 = { q: 'ts', type: 'month' }
    const dsExpected = [
      [1, 45], [1003, 23] 
    ]
    const msExpected = {
      cat: [[1003, 15], [1006, 8]],
      dog: [[1007, 5]],
    }
    const taskExpected = {
      task: [
        {1: 1, 2: 2, 3: 0, 4: 0 },
        {1: 1, 2: 2, 3: 0, 4: 0 },
        {1: 1, 2: 2, 3: 0, 4: 0 },
        {1: 1, 2: 2, 3: 0, 4: 0 },
        {1: 1, 2: 2, 3: 0, 4: 0 },
        {1: 1, 2: 2, 3: 0, 4: 0 },
        {1: 1, 2: 2, 3: 0, 4: 0 },
        {1: 1, 2: 2, 3: 0, 4: 0 },
      ]
    }


    request.get.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: dsExpected,
      })
    })

    getStats(params1).then(({ result }) => {
      expect(result).toEqual(dsExpected)
    })

    request.get.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: msExpected,
      })
    })

    getStats(params2).then(({ result }) => {
      expect(result).toEqual(msExpected)
    })
    request.get.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: dsExpected,
      })
    })
    getStats(params3).then(({ result }) => {
      expect(result).toEqual(dsExpected)
    })
    request.get.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: taskExpected,
      })
    })
    getStats(params4).then(({ result }) => {
      expect(result).toEqual(taskExpected)
    })

    request.get.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: taskExpected,
      })
    })
    getStats(params5).then(({ result }) => {
      expect(result).toEqual(taskExpected)
    })
  })
})