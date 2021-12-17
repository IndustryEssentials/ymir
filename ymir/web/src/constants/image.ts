import t from '@/utils/t'

export const TYPES = Object.freeze({
  TRAINING: 1,
  MINING: 2,
})

export const STATES = Object.freeze({
  PENDING: 1,
  DONE: 2,
  ERROR: 3,
})

export const getImageTypeLabel = (type: number | undefined) => {
  const labels = Object.freeze({
    [TYPES.TRAINING]: t('image.type.train'),
    [TYPES.MINING]: t('image.type.mining'),
  })
  return typeof type !== 'undefined' ? labels[type] : labels
}
