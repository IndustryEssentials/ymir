import request from '@/utils/request'
import { TASKTYPES } from '@/constants/task'
import { randomNumber } from '@/utils/number'
import { generateName } from '@/utils/string'
import { FilterParams, FusionParams, InferenceParams, LabelParams, MergeParams, MiningParams, TaskParams, TasksQuery, TrainingParams } from './task.d'

/**
 * get (or filter) task list
 * @export
 * @param {TasksQuery} { stages = [], datasets = [], name, type, state, start_time, end_time, offset = 0, limit = 20, is_desc, order_by }
 * @return {*}
 */
export function getTasks({ stages = [], datasets = [], name, type, state, start_time, end_time, offset = 0, limit = 20, is_desc, order_by }: TasksQuery) {
  const stageIds = stages.toString() || null
  const datasetIds = datasets.toString() || null
  return request.get('/tasks/', {
    params: {
      name,
      type,
      state,
      start_time,
      end_time,
      offset,
      limit,
      is_desc,
      order_by,
      model_stage_ids: stageIds,
      dataset_ids: datasetIds,
    },
  })
}

/**
 * get single task
 * @param {number} id  task id
 */
export function getTask(id: number) {
  return request.get(`/tasks/${id}`)
}

/**
 * stop task( and get label data for label task)
 * @param {number} id
 * @param {boolean} [fetch_result] fetch result or not
 */
export function stopTask(id: number, fetch_result: boolean = false) {
  return request.post(`/tasks/${id}/terminate`, { fetch_result })
}

/**
 * update task, only support task name now
 * @param {number} id
 * @param {string} name
 */
export function updateTask(id: number, name: string) {
  return request({
    method: 'PATCH',
    url: `/tasks/${id}`,
    data: { name },
  })
}

/**
 * create fusion task
 * @export
 * @param {FusionParams} {
 *   project_id,
 *   group_id,
 *   dataset,
 *   include_datasets = [],
 *   mining_strategy,
 *   include_strategy = 2,
 *   exclude_result,
 *   exclude_datasets = [],
 *   include = [],
 *   exclude = [],
 *   samples,
 *   description,
 * }
 */
export function fusion({
  project_id,
  group_id,
  dataset,
  include_datasets = [],
  mining_strategy,
  include_strategy = 2,
  exclude_result,
  exclude_datasets = [],
  include = [],
  exclude = [],
  samples,
  description,
}: FusionParams) {
  return request.post('/tasks/', {
    name: generateName('fusion'),
    type: TASKTYPES.FUSION,
    project_id,
    parameters: {
      task_type: 'fusion',
      project_id,
      include_datasets,
      exclude_datasets,
      mining_strategy,
      exclude_last_result: exclude_result,
      dataset_group_id: group_id,
      dataset_id: dataset,
      merge_strategy: include_strategy,
      include_labels: include,
      exclude_labels: exclude,
      sampling_count: samples || 0,
      description,
    },
  })
}

/**
 * create merge task
 * @export
 * @param {MergeParams} { projectId, group, name, datasets = [], strategy = 2, excludes = [], description }
 */
export function merge({ projectId, group, name, datasets = [], strategy = 2, excludes = [], description }: MergeParams) {
  return request.post('/tasks/', {
    name: generateName('merge'),
    type: TASKTYPES.MERGE,
    project_id: projectId,
    parameters: {
      task_type: 'merge',
      project_id: projectId,
      include_datasets: datasets,
      exclude_datasets: excludes,
      dataset_group_name: name,
      dataset_group_id: group,
      merge_strategy: strategy,
      description,
    },
  })
}
/**
 * create filter task
 * @export
 * @param {FilterParams} { projectId, dataset, name, includes, excludes, samples, description }
 */
export function filter({ projectId, dataset, name, includes, excludes, samples, description }: FilterParams) {
  return request.post('/tasks/', {
    name: generateName('filter'),
    type: TASKTYPES.FILTER,
    project_id: projectId,
    parameters: {
      dataset_group_name: name,
      task_type: 'filter',
      project_id: projectId,
      dataset_id: dataset,
      include_labels: includes,
      exclude_labels: excludes,
      sampling_count: samples,
      description,
    },
  })
}
/**
 * create label task
 * @export
 * @param {LabelParams} { projectId, groupId, name, datasetId, keywords, keepAnnotations, doc, description }
 */
export function label({ projectId, groupId, name, datasetId, keywords, keepAnnotations, doc, description }: LabelParams) {
  return request.post('/tasks/', {
    name: generateName('task_label'),
    type: TASKTYPES.LABEL,
    project_id: projectId,
    parameters: {
      task_type: 'label',
      dataset_group_name: name,
      dataset_group_id: groupId,
      dataset_id: datasetId,
      keywords,
      labellers: ['hide@label.com'],
      extra_url: doc,
      annotation_type: keepAnnotations || undefined,
      description,
    },
  })
}

/**
 * create training task
 * @export
 * @param {TrainingParams} { openpai, description, projectId, datasetId, keywords, testset, config, trainType, strategy, modelStage, image }
 */
export function train({ openpai, description, projectId, datasetId, keywords, testset, config, trainType, strategy, modelStage, image }: TrainingParams) {
  const model = modelStage ? modelStage[0] : undefined
  const stageId = modelStage ? modelStage[1] : undefined
  return request.post('/tasks/', {
    name: generateName('task_train'),
    project_id: projectId,
    result_description: description,
    type: TASKTYPES.TRAINING,
    docker_image_config: { ...config, openpai_enable: openpai },
    parameters: {
      task_type: 'training',
      strategy,
      dataset_id: datasetId,
      validation_dataset_id: testset,
      keywords,
      train_type: trainType,
      model_id: model,
      model_stage_id: stageId,
      docker_image_id: image,
    },
  })
}

/**
 * @description
 * @export
 * @param {MiningParams} { openpai, description, projectId, datasetId, modelStage, topk, config, name, image }
 */
export function mine({ openpai, description, projectId, datasetId, modelStage, topk, config, name, image }: MiningParams) {
  const model = modelStage[0]
  const stageId = modelStage[1]
  return request.post('/tasks/', {
    type: TASKTYPES.MINING,
    project_id: projectId,
    result_description: description,
    name: generateName('task_mining'),
    docker_image_config: { ...config, openpai_enable: openpai },
    parameters: {
      task_type: 'mining',
      model_id: model,
      model_stage_id: stageId,
      dataset_id: datasetId,
      dataset_group_name: name,
      top_k: topk,
      docker_image_id: image,
    },
  })
}

/**
 * create inference task
 * @export
 * @param {InferenceParams} { name, projectId, datasets, stages = [], config, image, openpai, description }
 */
export function infer({ name, projectId, dataset, stage: [model, mstage], config, image, openpai, description }: InferenceParams) {
  const params = {
    name,
    type: TASKTYPES.INFERENCE,
    project_id: projectId,
    result_description: description,
    docker_image_config: { ...config, openpai_enable: openpai },
    parameters: {
      task_type: 'infer',
      model_id: model,
      model_stage_id: mstage,
      dataset_id: dataset,
      docker_image_id: image,
    },
  }
  return request.post('/tasks/', params)
}
