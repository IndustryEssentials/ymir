import { BackendData } from "@/interface/common"
import { Image, InferConfig } from '@/interface/image'
import { format } from "@/utils/date"

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

export function imageIsPending(state: number) {
  return state === STATES.PENDING
}

export const getImageTypeLabel = (functions: number[] = []) => {
  const labels = {
    [TYPES.UNKOWN]: 'image.type.unkown',
    [TYPES.TRAINING]: 'image.type.train',
    [TYPES.MINING]: 'image.type.mining',
    [TYPES.INFERENCE]: 'image.type.inference',
  }

  return functions.map(func => labels[func])
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
    [STATES.PENDING]: 'image.state.pending',
    [STATES.DONE]: 'image.state.done',
    [STATES.ERROR]: 'image.state.error',
  }
  return labels[state]
}

export function transferImage(data: BackendData): Image {
  return {
    id: data.id,
    name: data.name,
    state: data.state,
    functions: (data.configs || []).map((config: InferConfig) => config.type),
    configs: (data.configs || []).map((func: BackendData) => ({ ...func, liveCode: func.enable_livecode })),
    url: data.url,
    isShared: data.is_shared,
    related: data.related,
    description: data.description,
    createTime: format(data.create_datetime),
  }
}
