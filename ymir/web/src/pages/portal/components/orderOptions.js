
import t from '@/utils/t'
export const ORDER = Object.freeze({
  map: 1,
  hot: 2,
})

export const options = [
  { value: ORDER.hot, label: t('common.hot') },
  { value: '', label: t('common.latest') },
]