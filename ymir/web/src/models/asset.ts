import { evaluationTags } from '@/constants/prediction'
import { transferAsset } from '@/constants/asset'
import { getAsset, getAssets } from '@/services/asset'
import { createEffect, createReducers } from './_utils'
type AssetsPayload = Omit<YParams.AssetQueryParams, 'cm'> & { datasetKeywords?: string[]; cm: evaluationTags }
type AssetPayload = { pid: number; id: number; type?: number; hash: string }

const reducersList = [
  { name: 'UpdateAssets', field: 'assets' },
  { name: 'UpdateAsset', field: 'asset' },
]

const AssetModel: YStates.AssetStore = {
  namespace: 'asset',
  state: {
    assets: {},
    asset: {},
  },
  effects: {
    getAssets: createEffect<AssetsPayload>(function* ({ payload }, { call, put }) {
      console.log('payload:', payload)
      const { cm, datasetKeywords, ...params } = payload
      const left = [evaluationTags.fp, evaluationTags.fn]
      let paramCm: evaluationTags | undefined = cm
      if (cm && !left.includes(cm)) {
        paramCm = undefined
        params.exclude = left
      }
      const { code, result } = yield call(getAssets, { cm: paramCm, ...params })
      if (code === 0) {
        const { items, total } = result as YStates.List<YModels.Asset>
        const keywords = [...new Set(items.map((item: { keywords: string[] }) => item.keywords).flat())]
        const assets = { items: items.map((asset: YModels.Asset) => transferAsset(asset, datasetKeywords || keywords)), total }

        yield put({
          type: 'UpdateAssets',
          payload: assets,
        })
        return assets
      }
    }),
    getAsset: createEffect<AssetPayload>(function* ({ payload }, { call, put }) {
      const { pid, id, type, hash } = payload
      const { code, result } = yield call(getAsset, pid, id, type, hash)
      if (code === 0) {
        const asset = transferAsset(result)
        yield put({
          type: 'UpdateAsset',
          payload: asset,
        })
        return asset
      }
    }),
  },
  reducers: createReducers(reducersList),
}

export default AssetModel
