import { getImage, getImages, delImage, createImage, updateImage, relateImage } from '@/services/image'
import { STATES, transferImage } from '@/constants/image'
import { createEffect, createReducers } from './_utils'
import { EditImage, Image as CreateImageParams, QueryParams } from '@/services/typings/image.d'
import { ObjectType } from '@/constants/objectType'
import { ImageStore } from '.'
import { Image } from '@/constants'

const reducers = [
  { name: 'UpdateImage', field: 'image' },
  { name: 'UpdateTotal', field: 'total' },
  { name: 'UpdateOfficial', field: 'official' },
]

const ImageModel: ImageStore = {
  namespace: 'image',
  state: {
    image: {},
    total: 0,
    official: undefined,
  },
  effects: {
    getImages: createEffect<QueryParams>(function* ({ payload }, { call, put }) {
      const { code, result } = yield call(getImages, payload)
      if (code === 0) {
        const { items, total } = result
        const images: Image[] = items.map(transferImage)
        yield put({
          type: 'UpdateImage',
          payload: images.reduce(
            (prev, image) => ({
              ...prev,
              [image.id]: image,
            }),
            {},
          ),
        })
        return { items: images, total }
      }
    }),
    getImage: createEffect<{ id: number; force?: boolean }>(function* ({ payload }, { call, put, select }) {
      const { id, force } = payload
      if (!force) {
        const cache = yield select(({ image }) => image.image[id])
        if (cache) {
          return cache
        }
      }
      const { code, result } = yield call(getImage, id)
      if (code === 0) {
        const image = transferImage(result)
        yield put({
          type: 'UpdateImage',
          payload: { [image.id]: image },
        })
        return image
      }
    }),
    delImage: createEffect<number>(function* ({ payload: id }, { call, put }) {
      const { code, result } = yield call(delImage, id)
      if (code === 0) {
        const image = transferImage(result)
        yield put({
          type: 'UpdateImage',
          payload: { [id]: null },
        })
        return image
      }
    }),
    createImage: createEffect<CreateImageParams>(function* ({ payload }, { call, put }) {
      const { code, result } = yield call(createImage, payload)
      if (code === 0) {
        // response as task
        return result
      }
    }),
    updateImage: createEffect<EditImage & { id: number }>(function* ({ payload }, { call, put }) {
      const { id, name, description } = payload
      const { code, result } = yield call(updateImage, id, { name, description })
      if (code === 0) {
        const image = transferImage(result)
        yield put({
          type: 'UpdateImage',
          payload: { [image.id]: image },
        })
        return image
      }
    }),
    relateImage: createEffect<{ id: number; relations: number[] }>(function* ({ payload }, { call, put }) {
      const { id, relations } = payload
      const { code, result } = yield call(relateImage, id, relations)
      if (code === 0) {
        const image = transferImage(result)
        yield put({
          type: 'UpdateImage',
          payload: { [image.id]: image },
        })
        return image
      }
    }),
    getValidImagesCount: createEffect<{ type?: ObjectType }>(function* ({ payload: { type } }, { put }) {
      const result = yield put.resolve({
        type: 'getImages',
        payload: {
          state: STATES.VALID,
          objectType: type,
        },
      })
      if (result?.total) {
        yield put({
          type: 'UpdateTotal',
          payload: result.total,
        })
        return result.total
      }
    }),
    batch: createEffect<number[]>(function* ({ payload: ids }, { put }) {
      const list = []
      for (let key = 0; key < ids.length; key++) {
        const id = ids[key]
        const image = yield put.resolve({
          type: 'getImage',
          payload: { id, force: true },
        })
        list.push(image)
      }
      return list
    }),
    getOfficialImage: createEffect<boolean>(function* ({ payload: force }, { put, select }) {
      const { official } = select(({ image }) => image)
      if (!force && official) {
        return official
      }
      const images = yield put.resolve({
        type: 'getImages',
        payload: {
          official: true,
        },
      })
      if (images?.items?.length) {
        const image = images.items[0]
        yield put({
          type: 'UpdateOfficial',
          payload: image,
        })
        return image
      }
    }),
  },
  reducers: createReducers(reducers),
}

export default ImageModel
