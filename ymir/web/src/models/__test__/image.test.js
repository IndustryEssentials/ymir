import image from "../image"
import { put, call, select } from "redux-saga/effects"
import { errorCode } from './func'

function equalObject(obj1, obj2) {
  expect(JSON.stringify(obj1)).toBe(JSON.stringify(obj2))
}

describe("models: image", () => {
  const product = (id) => ({ id })
  const products = (n) => Array.from({ length: n }, (item, index) => product(index + 1))
  it("reducers: UPDATE_IMAGES", () => {
    const state = {
      images: {},
    }
    const expected = {items: [1,2,3,4], total: 4}
    const action = {
      payload: expected,
    }
    const result = image.reducers.UPDATE_IMAGES(state, action)
    expect(result.images.total).toBe(expected.total)
  })
  it("reducers: UPDATE_IMAGE", () => {
    const state = {
      image: {},
    }
    const expected = { id: 10013 }
    const action = {
      payload: expected,
    }
    const result = image.reducers.UPDATE_IMAGE(state, action)
    expect(result.image.id).toBe(expected.id)
  })

  
  errorCode(image, 'getImages')
  errorCode(image, 'getImage')
  errorCode(image, 'delImage')
  errorCode(image, 'createImage')
  errorCode(image, 'updateImage')
  errorCode(image, 'shareImage')
  errorCode(image, 'relateImage')
  errorCode(image, 'getShareImages')

  it("effects: getImages -> success", () => {
    const saga = image.effects.getImages
    const creator = {
      type: "getImages",
      payload: {},
    }
    const images = products(9).map(image => ({ id: image, configs: [{ config: { anchor: '12,3,4'}, type: 1 }]}))
    const result = { items: images, total: images.length }

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result,
    })
    const end = generator.next()

    expect(end.value).toEqual({ items: images.map((image, index) => ({ ...image, functions: index === images.length ? [] : [1]})), total: images.length })
    expect(end.done).toBe(true)
  })
  it("effects: getShareImages -> success", () => {
    const saga = image.effects.getShareImages
    const creator = {
      type: "getShareImages",
      payload: {},
    }
    const images = products(9).map(image => ({ id: image, configs: [{ config: { anchor: '12,3,4'}, type: 1 }]}))
    const expected = { items: images, total: images.length }

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })

  it("effects: getImage", () => {
    const saga = image.effects.getImage
    const id = 10012
    const creator = {
      type: "getImage",
      payload: id,
    }
    const expected = { id, name: 'image001' }

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    const end = generator.next()

    expect(end.value).toEqual({ ...expected, functions: [] })
    expect(end.done).toBe(true)
  })
  it("effects: delImage", () => {
    const saga = image.effects.delImage
    const id = 10014
    const creator = {
      type: "delImage",
      payload: id,
    }
    const expected = { id, name: 'del_image_name' }

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    equalObject(expected, end.value)
    expect(end.done).toBe(true)
  })
  it("effects: createImage", () => {
    const saga = image.effects.createImage
    const id = 10015
    const expected = {id, name: 'new_image_name'}
    const creator = {
      type: "createImage",
      payload: { name: 'new_image_name', type: 1 },
    }

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    equalObject(expected, end.value)
    expect(end.done).toBe(true)
  })
  it("effects: updateImage", () => {
    const saga = image.effects.updateImage
    const creator = {
      type: "updateImage",
      payload: {id: 10011, name: 'new_image_name'},
    }
    const expected = {id: 10011, name: 'new_image_name'}

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    equalObject(expected, end.value)
    expect(end.done).toBe(true)
  })
  it("effects: shareImage", () => {
    const saga = image.effects.shareImage
    const creator = {
      type: "shareImage",
      payload: {id: 10011, name: 'new_image_name'},
    }
    const expected = {id: 10011, name: 'new_image_name'}

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    equalObject(expected, end.value)
    expect(end.done).toBe(true)
  })
  it("effects: relateImage", () => {
    const saga = image.effects.relateImage
    const creator = {
      type: "relateImage",
      payload: {id: 10011, name: 'new_image_name'},
    }
    const expected = {id: 10011, name: 'new_image_name'}

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    equalObject(expected, end.value)
    expect(end.done).toBe(true)
  })
})