import {
  getUploadUrl,
  getTensorboardLink,
  getHistory,
  getStats,
  getSysInfo,
} from '../common'
import { requestExample } from './func'

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
    requestExample(getHistory, params, expected, 'get')
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

    requestExample(getStats, params1, msExpected, 'get')
    requestExample(getStats, params2, dsExpected, 'get')
    requestExample(getStats, params3, dsExpected, 'get')
    requestExample(getStats, params4, taskExpected, 'get')
    requestExample(getStats, params5, taskExpected, 'get')
  })
  it('common:getSysInfo', () => {
    const expected = {
      gpu_count: 8,
    }
    requestExample(getSysInfo, {}, expected, 'get')
  })
})