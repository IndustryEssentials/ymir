import { getImage, getImages, delImage, createImage, updateImage, shareImage, relateImage, getShareImages } from '@/services/image'
import { transferImage } from '@/constants/image'
import { NormalReducer } from './_utils'

const reducers = {
  UPDATE_IMAGES: NormalReducer('images'),
  UPDATE_IMAGE: NormalReducer('image'),
}

export default {
  namespace: 'image',
  state: {
    images: {
      items: [],
      total: 0,
    },
    image: {},
  },
  effects: {
    *getImages({ payload }, { call, put }) {
      const { code, result } = yield call(getImages, payload)
      if (code === 0) {
        const { items, total } = result
        const images = items.map((image) => transferImage(image))
        const imageList = { items: images, total }
        yield put({
          type: 'UPDATE_IMAGES',
          payload: imageList,
        })
        yield put({
          type: 'UPDATE_IMAGE',
          payload: images.reduce(
            (prev, image) => ({
              ...prev,
              [image.id]: image,
            }),
            {},
          ),
        })
        return imageList
      }
    },
    *getShareImages({}, { call }) {
      const { code, result } = yield call(getShareImages)
      if (code === 0) {
        return result
      }
    },
    *getImage({ payload }, { call, put, select }) {
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
          type: 'UPDATE_IMAGE',
          payload: { [image.id]: image },
        })
        return image
      }
    },
    *delImage({ payload: id }, { call, put }) {
      const { code, result } = yield call(delImage, id)
      if (code === 0) {
        yield put({
          type: 'UPDATE_IMAGE',
          payload: { [id]: null },
        })
        return result
      }
    },
    *createImage({ payload }, { call, put }) {
      const { code, result } = yield call(createImage, payload)
      if (code === 0) {
        const image = transferImage(result)
        yield put({
          type: 'UPDATE_IMAGE',
          payload: { [image.id]: image },
        })
        return image
      }
    },
    *updateImage({ payload }, { call, put }) {
      const { id, name, description } = payload
      const { code, result } = yield call(updateImage, id, { name, description })
      if (code === 0) {
        const image = transferImage(result)
        yield put({
          type: 'UPDATE_IMAGE',
          payload: { [image.id]: image },
        })
        return image
      }
    },
    *shareImage({ payload }, { call, put }) {
      const { id, ...res } = payload
      const { code, result } = yield call(shareImage, id, res)
      if (code === 0) {
        const image = transferImage(result)
        yield put({
          type: 'UPDATE_IMAGE',
          payload: { [image.id]: image },
        })
        return image
      }
    },
    *relateImage({ payload }, { call, put }) {
      const { id, relations } = payload
      const { code, result } = yield call(relateImage, id, relations)
      if (code === 0) {
        const image = transferImage(result)
        yield put({
          type: 'UPDATE_IMAGE',
          payload: { [image.id]: image },
        })
        return image
      }
    },
  },
  reducers,
}
