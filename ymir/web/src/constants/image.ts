import { format } from '@/utils/date'

export enum TYPES {
  UNKOWN = 0,
  TRAINING = 1,
  MINING = 2,
  INFERENCE = 9,
}

export enum STATES {
  PENDING = 1,
  DONE = 3,
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

  return functions.map((func) => labels[func])
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

export function transferImage(data: YModels.BackendData): YModels.Image {
  const configs: YModels.DockerImageConfig[] = data.configs || []
  const getConfigAttr = <K extends keyof YModels.DockerImageConfig>(attr: K): YModels.DockerImageConfig[K][] => [
    ...new Set(configs.map((config) => config[attr])),
  ]
  const objectTypes = getConfigAttr('object_type').filter((t): t is YModels.ObjectType => !!t)
  const functions = getConfigAttr('type')
  return {
    id: data.id,
    name: data.name,
    state: data.state,
    errorCode: data.error_code,
    objectTypes,
    functions,
    configs,
    url: data.url,
    liveCode: data.enable_livecode,
    related: data.related,
    description: data.description,
    createTime: format(data.create_datetime),
  }
}

export const getConfig = (image: YModels.Image, type: number, objectType: number) =>
  image.configs.find((config) => config.type === type && (!config.object_type || config.object_type === objectType))
