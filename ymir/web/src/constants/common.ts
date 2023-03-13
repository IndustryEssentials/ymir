import storage from "@/utils/storage"

type Result = YModels.Dataset | YModels.Prediction | YModels.Model

export const HIDDENMODULES = {
  ITERATIONSWITCH: true,
  OPENPAI: true,
  LIVECODE: true,
}

export const INFER_DATASET_MAX_COUNT = 50000
export const INFER_CLASSES_MAX_COUNT = 20

export enum ResultStates {
  READY = 0,
  VALID = 1,
  INVALID = 2,
}

export enum actions {
  hide = 'hide',
  restore = 'unhide',
  del = 'delete',
}

export const OPENPAI_MAX_GPU_COUNT = 8

export function updateResultState(result: YModels.AllResult, tasks: YModels.BackendData) {
  const task = result?.task?.hash ? tasks[result.task.hash] : null
  if (!result || !task) {
    return result
  }
  return updateResultByTask(result, task)
}

export function updateResultByTask<T extends YModels.Result>(result: T, task?: YModels.ProgressTask): T | undefined {
  if (!result || !task) {
    return
  }
  if (ResultStates.VALID === task.result_state) {
    result.needReload = true
  }
  result.state = task.result_state
  result.progress = task.percent
  result.taskState = task.state
  result.task.state = task.state
  result.task.percent = task.percent
  return result
}

export function validState(state: number) {
  return ResultStates.VALID === state
}
export function invalidState(state: number) {
  return ResultStates.INVALID === state
}
export function readyState(state: number) {
  return ResultStates.READY === state
}
export const statesLabel = (state: ResultStates) => {
  const maps = {
    [ResultStates.READY]: 'dataset.state.ready',
    [ResultStates.VALID]: 'dataset.state.valid',
    [ResultStates.INVALID]: 'dataset.state.invalid',
  }
  return maps[state]
}

export function getVersionLabel(version: number) {
  return `V${version}`
}

export const getDeployUrl = () => getThirdUrl('DEPLOY_MODULE_URL')

export const getPublicImageUrl = () => getThirdUrl('PUBLIC_IMAGE_URL')

/**
 * @description generate tensorboard link
 * @export
 * @param {(string | string[])} [hashs=[]]
 * @return {*} 
 */
export function getTensorboardLink(hashs: string | string[] = []) {
  if (!Array.isArray(hashs)) {
    hashs = [hashs]
  }
  const query = hashs.filter(hash => hash).join('|')
  return `/tensorboard/#scalars&regexInput=${query}`
}

const getThirdUrl = (field: string) => {
  const config = window?.baseConfig || {}
  const url = config[field]
  const onlyPort = /^\d+$/.test(url)
  return onlyPort ? `${location.protocol}//${location.hostname}:${url}` : url
}

export const getErrorCodeDocLink = (code: string | number = '') => `/docs/#/error-code-zh-CN?id=_${code}`

enum MergeStrategy {
  latest = 2,
  older = 3,
  stop = 1,
}

enum LabelAnnotationTypes {
  gt = 1,
  pred = 2,
}

export const getLabelAnnotationTypes = (isPred?: boolean) => {
  const prefix = 'task.label.form.keep_anno.'
  const type = isPred ? 'pred' : 'gt'
  const keepItem = { value: LabelAnnotationTypes[type], label: `${prefix}${type}`}
  return [
    keepItem,
    {value: undefined, label: `${prefix}none`},
  ]
}

export const getLabelAnnotationType = (type: LabelAnnotationTypes | undefined) => {
  const types = getLabelAnnotationTypes()
  const target = types.find(({ value }) => !value || value === type)
  return target?.label
}

export const getMergeStrategies = () => {
  const prefix = 'task.train.form.repeatdata'
  return [
    { value: MergeStrategy.latest, label: `${prefix}.latest` },
    { value: MergeStrategy.older, label: `${prefix}.original` },
    { value: MergeStrategy.stop, label: `${prefix}.terminate` },
  ]
}

export const getMergeStrategyLabel = (strategy: MergeStrategy | undefined) => {
  return strategy ? getMergeStrategies().find(({ value }) => value === strategy)?.label : undefined
}

export const getLabelToolUrl = () => {
  const base = '/label_tool/'
  const token = storage.get('access_token')
  return `${base}?token=${token}`
}
