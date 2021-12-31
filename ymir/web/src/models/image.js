import { 
  getImage, 
  getImages,
  delImage,
  createImage,
  updateImage,
  shareImage,
  relateImage,
} from "@/services/image"

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
        yield put({
          type: "UPDATE_IMAGES",
          payload: result,
        })
      }
      return result
    },
    *batchImages({ payload }, { call, put }) {
      const { code, result } = yield call(batchImages, payload)
      if (code === 0) {
        return result.items
      }
    },
    *getImage({ payload }, { call, put }) {
      const { code, result } = yield call(getImage, payload)
      if (code === 0) {
        const pa = result.parameters || {}
        const trainSets = pa?.include_train_datasets || []
        const testSets = pa?.include_validation_datasets || []
        const ids = [
          ...trainSets,
          ...testSets,
        ]
        if (ids.length) {
          const datasets = yield put.resolve({ type: 'dataset/batchDatasets', payload: ids })
          if (datasets && datasets.length) {
            result['trainSets'] = trainSets.map(sid => datasets.find(ds => ds.id === sid))
            result['testSets'] = testSets.map(sid => datasets.find(ds => ds.id === sid))
          }
        }
        yield put({
          type: "UPDATE_IMAGE",
          payload: result,
        })
      }
      return result
    },
    *delImage({ payload }, { call, put }) {
      const { code, result } = yield call(delImage, payload)
      return result
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
      console.log('model share image: ', id, res)
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
    *verify({ payload }, { call }) {
      const { id, urls } = payload
      console.log('image of images: ', id, urls)
      const { code, result } = yield call(verify, id, urls)
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
