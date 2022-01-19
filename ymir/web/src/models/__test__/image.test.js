import image from "../image"
import { put, call, select } from "redux-saga/effects"

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

  it("effects: getImages", () => {
    const saga = image.effects.getImages
    const creator = {
      type: "getImages",
      payload: {},
    }
    const expected = { items: [1, 2, , 3, 4], total: 4 }

    const generator = saga(creator, { put, call })
    generator.next()
    const response = generator.next({
      code: 0,
      result: expected,
    })
    const end = generator.next()

    expect(end.value.total).toBe(4)
    expect(end.value.items.length).toBe(5)
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

    equalObject(expected, end.value)
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