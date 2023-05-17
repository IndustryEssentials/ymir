import image from '../image'
import { put, call, select } from 'redux-saga/effects'
import { errorCode } from './func'
import { transferImage } from '../../constants/image'

describe('models: image', () => {
  const product = (id) => ({ id })
  const products = (n) => Array.from({ length: n }, (item, index) => product(index + 1))
  it('reducers: UPDATE_IMAGES', () => {
    const state = {
      images: {},
    }
    const expected = { items: [1, 2, 3, 4], total: 4 }
    const action = {
      payload: expected,
    }
    const result = image.reducers.UPDATE_IMAGES(state, action)
    expect(result.images.total).toBe(expected.total)
  })
  it('reducers: UPDATE_IMAGE', () => {
    const state = {
      image: {},
    }
    const id = 10013
    const expected = { [id]: { id: 10013 } }
    const action = {
      payload: expected,
    }
    const result = image.reducers.UPDATE_IMAGE(state, action)
    expect(expected).toEqual(result.image)
  })

  errorCode(image, 'getImages')
  errorCode(image, 'getImage', { id: 222111, force: true })
  errorCode(image, 'delImage')
  errorCode(image, 'createImage')
  errorCode(image, 'updateImage')
  errorCode(image, 'shareImage')
  errorCode(image, 'relateImage')
  errorCode(image, 'getShareImages')

  it('effects: getImages -> success', () => {
    const saga = image.effects.getImages
    const creator = {
      type: 'getImages',
      payload: {},
    }
    const images = products(9).map((image) => ({ id: image, configs: [{ config: { anchor: '12,3,4' }, type: 1 }] }))
    const result = { items: images, total: images.length }
    const expected = { items: images.map((img) => transferImage(img)), total: images.length }

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result,
    })
    generator.next()
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it('effects: getShareImages -> success', () => {
    const saga = image.effects.getShareImages
    const creator = {
      type: 'getShareImages',
      payload: {},
    }
    const images = products(9).map((image) => ({ id: image, configs: [{ config: { anchor: '12,3,4' }, type: 1 }] }))
    const expected = { items: images.map((image) => transferImage(image)), total: images.length }

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })

  it('effects: getImage', () => {
    const saga = image.effects.getImage
    const id = 10012
    const creator = {
      type: 'getImage',
      payload: { id },
    }
    const result = { id, name: 'image001' }
    const expected = transferImage(result)

    const generator = saga(creator, { put, call, select })
    generator.next()
    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it('effects: delImage', () => {
    const saga = image.effects.delImage
    const id = 10014
    const creator = {
      type: 'delImage',
      payload: id,
    }
    const result = { id, name: 'del_image_name' }
    const expected = transferImage(result)

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result,
    })
    const end = generator.next()

    expect(expected).toEqual(end.value)
    expect(end.done).toBe(true)
  })
  it('effects: createImage', () => {
    const saga = image.effects.createImage
    const id = 10015
    const result = { id, name: 'new_image_name' }
    const creator = {
      type: 'createImage',
      payload: { name: 'new_image_name', type: 1 },
    }

    const expected = transferImage(result)

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result,
    })
    const end = generator.next()

    expect(expected).toEqual(end.value)
    expect(end.done).toBe(true)
  })
  it('effects: updateImage', () => {
    const saga = image.effects.updateImage
    const result = { id: 10011, name: 'new_image_name' }
    const creator = {
      type: 'updateImage',
      payload: result,
    }
    const expected = transferImage(result)

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result,
    })
    const end = generator.next()

    expect(expected).toEqual(end.value)
    expect(end.done).toBe(true)
  })
  it('effects: shareImage', () => {
    const saga = image.effects.shareImage
    const result = { id: 10011, name: 'new_image_name' }
    const creator = {
      type: 'shareImage',
      payload: result,
    }
    const expected = transferImage(result)

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result,
    })
    const end = generator.next()

    expect(expected).toEqual(end.value)
    expect(end.done).toBe(true)
  })
  it('effects: relateImage', () => {
    const saga = image.effects.relateImage
    const result = { id: 10011, name: 'new_image_name' }
    const creator = {
      type: 'relateImage',
      payload: result,
    }
    const expected = transferImage(result)

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result,
    })
    const end = generator.next()

    expect(expected).toEqual(end.value)
    expect(end.done).toBe(true)
  })
})
