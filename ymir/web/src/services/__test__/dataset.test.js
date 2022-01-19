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
} from "../dataset"
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

describe("service: dataset", () => {



  it("getDataset -> success", () => {
    const id = 641
    const expected = { id, name: 'datasetname00345' }
    getRequestResponseOnce(expected, 'get')

    getDataset(id).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.name).toBe(expected.name)
      expect(result.id).toBe(expected.id)
    })
  })
  it("getDataset -> params validate failed", () => {
    getRequestResponseOnce(null, 'get', 1002)

    getDataset().then(({ code, result }) => {
      expect(code).toBe(1002)
      expect(result).toBeNull()
    })
  })

  it("getDatasets -> success -> all filter conditions", () => {
    const params = { name: 'searchname', type: 1, start_time: 0, end_time: 0, limit: 20, offset: 0 }
    const expected = products(4)

    getRequestResponseOnce({
      items: expected,
      total: expected.length
    }, 'get')
    getDatasets(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.items).toEqual(expected)
      expect(result.total).toBe(expected.length)
    })
  })

  it("getDatasets -> success -> filter name", () => {
    const params = { name: 'partofname' }
    const expected = products(2)

    getRequestResponseOnce({
      items: expected,
      total: expected.length
    }, 'get')
    getDatasets(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.items).toEqual(expected)
      expect(result.total).toBe(expected.length)
    })
  })

  it("getDatasets -> success -> none filter conditions", () => {
    const params = {}
    const expected = products(5)

    getRequestResponseOnce({
      items: expected,
      total: expected.length
    }, 'get')
    getDatasets(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.items).toEqual(expected)
      expect(result.total).toBe(expected.length)
    })
  })

  it("getDatasets -> success -> all filter conditions", () => {
    const params = { type: 1, start_time: 0, end_time: 0, limit: 20, offset: 40 }
    const expected = products(5)

    getRequestResponseOnce({
      items: expected,
      total: expected.length
    }, 'get')
    getDatasets(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.items).toEqual(expected)
      expect(result.total).toBe(expected.length)
    })
  })

  it("batchDatasets -> success", () => {
    const params = { ids: [1, 2, 3] }
    const expected = products(3)
    getRequestResponseOnce({
      items: expected,
      total: expected.length
    }, 'get')

    batchDatasets(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.items).toEqual(expected)
      expect(result.total).toBe(expected.length)
    })
  })

  it("delDataset -> success and ", () => {
    const id = 644
    const expected = { id }
    getRequestResponseOnce(expected)

    delDataset(id).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.id).toBe(id)
    })
  })

  it('delDataset -> can not find resource', () => {
    getRequestResponseOnce(null, null, 5001)
    delDataset().then(({ code, result }) => {
      expect(code).toBe(5001)
      expect(result).toBeNull()
    })
  })
  it("createDataset -> success", () => {
    const id = 646
    const datasets = { name: 'new dataset' }
    const expected = { id, ...datasets }
    getRequestResponseOnce(expected, 'post')

    createDataset(datasets).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.id).toBe(id)
      expect(result.name).toBe(expected.name)
    })
  })
  it("createDataset -> user logouted", () => {
    const datasets = { name: 'new dataset' }
    getRequestResponseOnce(null, 'post', 1004)
    createDataset(datasets).then(({ code, result }) => {
      expect(code).toBe(1004)
      expect(result).toBeNull()
    })
  })
  it("createDataset -> params validate failed", () => {
    getRequestResponseOnce(null, 'post', 1002)

    createDataset().then(({ code, result }) => {
      expect(code).toBe(1002)
      expect(result).toBeNull()
    })
  })

  it("updateDataset -> success", () => {
    const id = 647
    const name = 'new name of dataset'
    const expected = { id, name }
    getRequestResponseOnce(expected, null)


    updateDataset(id, name).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.id).toBe(id)
      expect(result.name).toBe(name)
    })
  })

  it("updateDataset -> dulplicated name", () => {
    const id = 648
    const name = 'dulplicated name'
    getRequestResponseOnce(null, null, 4002)

    updateDataset(id, name).then(({ code, result }) => {
      expect(code).toBe(4002)
      expect(result).toBeNull()
    })
  })

  it("updateDataset -> params validate failed", () => {
    getRequestResponseOnce(null, null, 1002)

    updateDataset().then(({ code, result }) => {
      expect(code).toBe(1002)
      expect(result).toBeNull()
    })
  })

  it("getAssetsOfDataset -> success", () => {
    const params = { id: 642 }
    const expected = products(11)
    getRequestResponseOnce({
      items: expected,
      total: expected.length,
    }, 'get')

    getAssetsOfDataset(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.items).toEqual(expected)
      expect(result.total).toBe(expected.length)
    })
  })

  it("getAssetsOfDataset -> success with keywords", () => {
    const params = { id: 642, keyword: 83, limit: 20, offset: 0, }
    const expected = products(7)
    getRequestResponseOnce({
      items: expected,
      total: expected.length,
    }, 'get')

    getAssetsOfDataset(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.items).toEqual(expected)
      expect(result.total).toBe(expected.length)
    })
  })

  it("getAsset -> success", () => {
    const hash = "643"
    const expected = { hash, url: '/path/to/asset/image', annotations: [{ keyword: 'cat', box: [234, 34, 200, 403] }] }
    getRequestResponseOnce(expected, 'get')

    getAsset(hash).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.url).toBe(expected.url)
      expect(result.hash).toBe(hash)
    })
  })

  it('getAsset -> can not find resource', () => {
    getRequestResponseOnce(null, 'get', 5001)

    getAsset().then(({ code, result }) => {
      expect(code).toBe(5001)
      expect(result).toBeNull()
    })
  })

  it("getInternalDataset -> success", () => {
    const expected = products(11)
    getRequestResponseOnce({
      items: expected,
      total: expected.length,
    }, 'get')

    getInternalDataset().then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.items).toEqual(expected)
      expect(result.total).toBe(expected.length)
    })
  })
})
