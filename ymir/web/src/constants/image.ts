import t from '@/utils/t'

export const TYPES = Object.freeze({
  UNKOWN: 0,
  TRAINING: 1,
  MINING: 2,
  INFERENCE: 9,
})

export const STATES = Object.freeze({
  PENDING: 1,
  DONE: 3,
  ERROR: 4,
})

export function imageIsPedding (state: number) {
  return state === STATES.PENDING
}

export const getImageTypeLabel = (functions: number[] | null) => {

  const labels = {
    [TYPES.UNKOWN]: t('image.type.unkown'),
    [TYPES.TRAINING]: t('image.type.train'),
    [TYPES.MINING]: t('image.type.mining'),
    [TYPES.INFERENCE]: t('image.type.inference'),
  }

  return functions?.map(func => labels[func])
}

/**
 * get image state label, default: ''
 * @param {number} state image state
 * @returns 
 */
export const getImageStateLabel = (state: number | undefined) => {
  if (!state) {
    return ''
  }
  const labels = {
    [STATES.PENDING]: t('image.state.pending'),
    [STATES.DONE]: t('image.state.done'),
    [STATES.ERROR]: t('image.state.error'),
  }
  return labels[state]
}
