import request from '@/utils/request'

import {
  getUploadUrl,
  getKeywords,
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
    const params = { q: 'ds', limit: 7 }
    const expected = {
      model: {},
      dataset: {},
      task: {},
    }
    request.get.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: expected,
      })
    })

    getStats(params).then(({ result }) => {
      expect(result).toEqual(expected)
    })
  })
})