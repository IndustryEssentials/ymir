import { 
getDataset,
getDatasets,
batchDatasets,
getAssetsOfDataset,
getAsset,
delDataset,
createDataset,
updateDataset,
getInternalDataset,
importDataset,
 } from "../dataset"
 import request from '@/utils/request'

 jest.mock('@/utils/request', () => {
   const req = jest.fn()
   req.get = jest.fn()
   req.post = jest.fn()
   return req
 })

describe("service: dataset", () => {

  
  const product = (id) => ({ id })
  const products = (n) => Array.from({ length: n }, (item, index) => product(index + 1))

  it("getDataset -> success", () => {
    const id = "641"
    const expected = { id, name: 'datasetname00345' }
    request.get.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: expected,
      })
    })

    getDataset(id).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.name).toBe(expected.name)
      expect(result.id).toBe(expected.id)
    })
  })

  it("getDatasets -> success", () => {
    const params = { name: 'searchname', type: 1, start_time: 0, end_time: 0, limit: 20, offset: 0 }
    const expected = products(9)
    request.get.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: {
          items: expected,
          total: expected.length,
        },
      })
    })

    getDatasets(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.items).toEqual(expected)
      expect(result.total).toBe(expected.length)
    })
  })

  it("batchDatasets -> success", () => {
    const params = { ids: [1,2,3] }
    const expected = products(3)
    request.get.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: {
          items: expected,
          total: expected.length,
        },
      })
    })

    batchDatasets(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.items).toEqual(expected)
      expect(result.total).toBe(expected.length)
    })
  })

  it("getAssetsOfDataset -> success", () => {
    const params = {
      id: "642",
      keyword: 83,
      limit: 20,
      offset: 0,
    }
    const expected = products(11)
    request.get.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: {
          items: expected,
          total: expected.length,
        },
      })
    })

    getAssetsOfDataset(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.items).toEqual(expected)
      expect(result.total).toBe(expected.length)
    })
  })
  it("getInternalDataset -> success", () => {
    const expected = products(11)
    request.get.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: {
          items: expected,
          total: expected.length,
        },
      })
    })

    getInternalDataset().then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.items).toEqual(expected)
      expect(result.total).toBe(expected.length)
    })
  })
})
