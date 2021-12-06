import {
  getModels, 
  batchModels,
  getModel,
  delModel,
  createModel,
  updateModel,
} from "../model"
import request from '@/utils/request'

jest.mock('@/utils/request', () => {
  const req = jest.fn()
  req.get = jest.fn()
  req.post = jest.fn()
  return req
})

describe("service: models", () => {
  it("getModels -> success", () => {
    const params = {
      name: 'testname',
      type: 1,
      start_time: 123942134,
      end_time: 134123434,
      offset: 0,
      limit: 20,
      sort_by_map: false,
    }
    const expected = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    request.get.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: {
          items: expected,
          total: expected.length,
        },
      })
    })

    getModels(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.items).toEqual(expected)
      expect(result.total).toBe(expected.length)
    })
  })
  it("batchModels -> success", () => {
    const params = [1,2,3]
    const expected = [11, 21, 31]
    request.get.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: {
          items: expected,
          total: expected.length,
        },
      })
    })

    batchModels(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.items).toEqual(expected)
      expect(result.total).toBe(expected.length)
    })
  })
  it("getModel -> success", () => {
    const id = 623
    const expected = {
      id,
      name: '63modelname',
    }
    request.get.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: expected,
      })
    })

    getModel(id).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.id).toBe(id)
      expect(result.name).toBe(expected.name)
    })
  })

  it("delModel -> success", () => {
    const id = 638
    const expected = "ok"
    request.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: expected,
      })
    })

    delModel(id).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result).toBe(expected)
    })
  })
  it("updateModel -> success", () => {
    const id = 637
    const name = 'newnameofmodel'
    const expected = { id, name }
    request.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: expected,
      })
    })

    updateModel(id, name).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.id).toEqual(id)
      expect(result.name).toEqual(name)
    })
  })
  it("createModel -> success", () => {
    const params = {
      name: 'newmodel',
    }
    const expected = "ok"
    request.post.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: expected,
      })
    })

    createModel(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result).toBe(expected)
    })
  })
})
