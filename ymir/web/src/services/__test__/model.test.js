import {
  getModels,
  batchModels,
  getModel,
  delModel,
  createModel,
  updateModel,
  verify,
} from "../model"
import request from '@/utils/request'

jest.mock('@/utils/request', () => {
  const req = jest.fn()
  req.get = jest.fn()
  req.post = jest.fn()
  return req
})

const product = (id) => ({ id })
const products = (n) => Array.from({ length: n }, (item, index) => product(index + 1))
const response = (result, code = 0) => ({ code, result })
const getRequestResponseOnce = (result, method = '', code = 0) => 
  (method ? request[method] : request).mockImplementationOnce(() => Promise.resolve(response(result, code)))

describe("service: models", () => {
  it("getModels -> success", () => {
    const params = { name: 'testname', type: 1, start_time: 123942134, end_time: 134123434, offset: 0, limit: 20, sort_by_map: false, }
    const expected = products(15)
    getRequestResponseOnce({
      items: expected,
      total: expected.length,
    }, 'get')

    getModels(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.items).toEqual(expected)
      expect(result.total).toBe(expected.length)
    })
  })
  it("batchModels -> success", () => {
    const params = [1, 2, 3]
    const expected = [11, 21, 31]
    getRequestResponseOnce({
      items: expected,
      total: expected.length,
    }, 'get')

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
    getRequestResponseOnce(expected, 'get')

    getModel(id).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.id).toBe(id)
      expect(result.name).toBe(expected.name)
    })
  })

  it("delModel -> success", () => {
    const id = 638
    const expected = "ok"
    getRequestResponseOnce(expected)

    delModel(id).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result).toBe(expected)
    })
  })
  it("updateModel -> success", () => {
    const id = 637
    const name = 'newnameofmodel'
    const expected = { id, name }
    getRequestResponseOnce(expected)

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
    getRequestResponseOnce(expected, 'post')

    createModel(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result).toBe(expected)
    })
  })
  it("veirfy -> success", () => {
    const params = { model_id: 754, image_urls: ['/path/to/image'], image: 'dockerimage:latest' }
    const expected = "ok"
    getRequestResponseOnce(expected, 'post')

    verify(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result).toBe(expected)
    })
  })
})
