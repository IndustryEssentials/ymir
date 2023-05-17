import {
  getImages,
  getImage,
  delImage,
  createImage,
  updateImage,
  relateImage,
} from "../image"
import { product, products, requestExample } from './func'

describe("service: images", () => {
  it("getImages -> success", () => {
    const params = { name: 'testname', type: 1, start_time: 123942134, end_time: 134123434, offset: 0, limit: 20, sort_by_map: false, }
    const expected = products(15)
    requestExample(getImages, params, { items: expected, total: expected.length }, 'get')
  })
  it("getImage -> success", () => {
    const id = 623
    const expected = {
      id,
      name: '63imagename',
    }
    requestExample(getImage, id, expected, 'get')
  })

  it("delImage -> success", () => {
    const id = 638
    const expected = "ok"
    requestExample(delImage, id, expected)
  })
  it("updateImage -> success", () => {
    const id = 637
    const name = 'newnameofimage'
    const expected = { id, name }
    requestExample(updateImage, [id, name], expected)
  })
  it("createImage -> success", () => {
    const params = {
      name: 'newimage',
    }
    const expected = "ok"
    requestExample(createImage, params, expected, 'post')
  })
  it("relateImage -> success", () => {
    const id = 857
    const relations = [34, 53, 6]
    const expected = "ok"
    requestExample(relateImage, [id, relations], expected)
  })
})
