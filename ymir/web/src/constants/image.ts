import { BackendData } from "@/interface/common"
import { Image, DockerImageConfig } from '@/interface/image'
import { format } from "@/utils/date"

export enum TYPES {
  UNKOWN = 0,
  TRAINING = 1,
  MINING = 2,
  INFERENCE = 9,
}

export enum STATES {
  PENDING = 1,
  DONE =3,
  ERROR = 4,
}

export function imageIsPending(state: number) {
  return state === STATES.PENDING
}

export const getImageTypeLabel = (functions: TYPES[] = []) => {
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
export const getImageStateLabel = (state: STATES | undefined) => {
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
  const configs: DockerImageConfig[] = data.configs || []
  return {
    id: data.id,
    name: data.name,
    state: data.state,
    functions: configs.map(config => config.type),
    configs,
    url: data.url,
    liveCode: data.enable_livecode,
    isShared: data.is_shared,
    related: data.related,
    description: data.description,
    createTime: format(data.create_datetime),
  }
}
