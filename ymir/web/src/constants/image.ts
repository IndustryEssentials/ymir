import { format } from '@/utils/date'
import { DockerImageConfig, Image } from '.'
import { ResultStates as STATES } from './common'
import { ObjectType } from './objectType'

export enum TYPES {
  UNKOWN = 0,
  TRAINING = 1,
  MINING = 2,
  INFERENCE = 9,
}

export { STATES }

export function imageIsPending(state: number) {
  return state === STATES.READY
}

export const getImageTypeLabel = (functions: TYPES[] = []) => {
  const labels = {
    [TYPES.UNKOWN]: 'image.type.unkown',
    [TYPES.TRAINING]: 'image.type.train',
    [TYPES.MINING]: 'image.type.mining',
    [TYPES.INFERENCE]: 'image.type.inference',
  }

  return functions.map((func) => labels[func])
}

/**
 * get image state label, default: ''
 * @param {number} state image state
 * @returns
 */
export const getImageStateLabel = (state?: STATES) => {
  if (typeof state === 'undefined') {
    return ''
  }
  const labels = {
    [STATES.READY]: 'image.state.pending',
    [STATES.VALID]: 'image.state.done',
    [STATES.INVALID]: 'image.state.error',
  }
  return labels[state]
}

export function transferImage(data: YModels.BackendData): Image {
  const configs: DockerImageConfig[] = data.configs || []
  const getConfigAttr = <K extends keyof DockerImageConfig>(attr: K): DockerImageConfig[K][] => [...new Set(configs.map((config) => config[attr]))]
  const objectTypes = getConfigAttr('object_type').filter((t): t is ObjectType => !!t) || []
  const functions = getConfigAttr('type')
  return {
    id: data.id,
    name: data.name,
    state: data.result_state,
    errorCode: data.error_code,
    objectTypes,
    functions,
    configs,
    url: data.url,
    official: data.is_official,
    liveCode: data.enable_livecode,
    related: data.related,
    description: data.description,
    createTime: format(data.create_datetime),
  }
}

export const getConfig = (image: Image, type: TYPES, objectType: ObjectType) =>
  image.configs.find((config) => config.type === type && config.object_type === objectType)
