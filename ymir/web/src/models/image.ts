import { getImage, getImages, delImage, createImage, updateImage, relateImage } from '@/services/image'
import { STATES, transferImage } from '@/constants/image'
import { createEffect, createReducers } from './_utils'
import { EditImage, Image, QueryParams } from '@/services/image.d'
import { ObjectType } from '@/constants/objectType'

const reducers = [
  { name: 'UpdateImage', field: 'image' },
  { name: 'UpdateTotal', field: 'total' },
]

const ImageModel: YStates.ImageStore = {
  namespace: 'image',
  state: {
    image: {},
    total: 0,
  },
  effects: {
    getImages: createEffect<QueryParams>(function* ({ payload }, { call, put }) {
      const { code, result } = yield call(getImages, payload)
      if (code === 0) {
        const { items, total } = result
        const images: YModels.Image[] = items.map(transferImage)
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
    createImage: createEffect<Image>(function* ({ payload }, { call, put }) {
      const { code, result } = yield call(createImage, payload)
      if (code === 0) {
        const image = transferImage(result)
        yield put({
          type: 'UpdateImage',
          payload: { [image.id]: image },
        })
        return image
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
    getValidImagesCount: createEffect<{ type?: ObjectType; example?: boolean }>(function* ({ payload: { type, example } }, { put }) {
      const result = yield put.resolve({
        type: 'getImages',
        payload: {
          state: STATES.DONE,
          type,
          example,
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
  },
  reducers: createReducers(reducers),
}

export default ImageModel
