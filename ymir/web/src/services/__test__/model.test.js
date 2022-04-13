import {
  getModels,
  getModelVersions,
  batchModels,
  getModel,
  delModel,
  importModel,
  updateModel,
  verify,
} from "../model"
import { product, products, requestExample } from './func'

describe("service: models", () => {
  it("getModels -> success", () => {
    const project_id = 5342
    const listParams = { offset: 0, limit: 20, }
    const queryParams = { name: 'testname', offset: 0, limit: 20, }
    const expected = products(15)
    requestExample(getModels, [project_id, listParams], { items: expected, total: expected.length }, 'get')
    requestExample(getModels, [project_id, queryParams], { items: expected, total: expected.length }, 'get')
  })
  it("getModelVersions -> success", () => {
    const gid = 5342
    const expected = products(15)
    requestExample(getModelVersions, gid, { items: expected, total: expected.length }, 'get')
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
  it("importModel -> success", () => {
    const params = {
      name: 'newmodel',
    }
    const expected = "ok"
    requestExample(importModel, params, expected, 'post')
  })
  it("veirfy -> success", () => {
    const params = { model_id: 754, image_urls: ['/path/to/image'], image: 'dockerimage:latest' }
    const expected = "ok"
    requestExample(verify, params, expected, 'post')
  })
})
