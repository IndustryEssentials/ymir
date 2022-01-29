import { 
  getImage, 
  getImages,
  delImage,
  createImage,
  updateImage,
  shareImage,
  relateImage,
  getShareImages,
} from "@/services/image"

function transferImage(image = {}) {
  return {
    ...image,
    functions: (image.configs || []).map(config => config.type),
  }
}

export default {
  namespace: "image",
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
        const images = items.map(image => transferImage(image))
        const imageList =  { items: images, total, }
        yield put({
          type: "UPDATE_IMAGES",
          payload: imageList,
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
    *getImage({ payload }, { call, put }) {
      const { code, result } = yield call(getImage, payload)
      if (code === 0) {
        const image = transferImage(result)
        yield put({
          type: "UPDATE_IMAGE",
          payload: image,
        })
        return image
      }
    },
    *delImage({ payload }, { call, put }) {
      const { code, result } = yield call(delImage, payload)
      if(code === 0) {
        return result
      }
    },
    *createImage({ payload }, { call, put }) {
      const { code, result } = yield call(createImage, payload)
      if (code === 0) {
        return result
      }
    },
    *updateImage({ payload }, { call, put }) {
      const { id, name, description } = payload
      const { code, result } = yield call(updateImage, id, { name, description, })
      if (code === 0) {
        return result
      }
    },
    *shareImage({ payload }, { call, put }) {
      const { id, ...res } = payload
      const { code, result } = yield call(shareImage, id, res)
      if (code === 0) {
        return result
      }
    },
    *relateImage({ payload }, { call, put }) {
      const { id, relations } = payload
      const { code, result } = yield call(relateImage, id, relations)
      if (code === 0) {
        return result
      }
    },
  },
  reducers: {
    UPDATE_IMAGES(state, { payload }) {
      return {
        ...state,
        images: payload
      }
    },
    UPDATE_IMAGE(state, { payload }) {
      return {
        ...state,
        image: payload
      }
    },
  },
}
