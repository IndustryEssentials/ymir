
import t from '@/utils/t'
export const ORDER = Object.freeze({
  map: 1,
  hot: 2,
})

export const options = [
  { value: '', label: t('最新') },
  { value: ORDER.hot, label: t('最热') },
]