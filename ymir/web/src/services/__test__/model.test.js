import {
  getModels,
  batchModels,
  getModel,
  delModel,
  createModel,
  updateModel,
  verify,
} from "../model"
import { product, products, requestExample } from './func'

describe("service: models", () => {
  it("getModels -> success", () => {
    const params = { name: 'testname', type: 1, start_time: 123942134, end_time: 134123434, offset: 0, limit: 20, sort_by_map: false, }
    const expected = products(15)
    requestExample(getModels, params, { items: expected, total: expected.length }, 'get')
  })
  it("batchModels -> success", () => {
    const params = [1, 2, 3]
    const expected = product(3)
    requestExample(batchModels, params, { items: expected, total: expected.length }, 'get')
  })
  it("getModel -> success", () => {
    const id = 623
    const expected = {
      id,
      name: '63modelname',
    }
    requestExample(getModel, id, expected, 'get')
  })

  it("delModel -> success", () => {
    const id = 638
    const expected = "ok"
    requestExample(delModel, id, expected)
  })
  it("updateModel -> success", () => {
    const id = 637
    const name = 'newnameofmodel'
    const expected = { id, name }
    requestExample(updateModel, [id, name], expected)
  })
  it("createModel -> success", () => {
    const params = {
      name: 'newmodel',
    }
    const expected = "ok"
    requestExample(createModel, params, expected, 'post')
  })
  it("veirfy -> success", () => {
    const params = { model_id: 754, image_urls: ['/path/to/image'], image: 'dockerimage:latest' }
    const expected = "ok"
    requestExample(verify, params, expected, 'post')
  })
})
