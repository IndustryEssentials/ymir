import { ObjectType } from '@/constants/project'
import request from '@/utils/request'

type QueryParams = {
  name?: string
  type?: ObjectType
  offset?: number
  limit?: number
}

type CreateParams = {
  name: string
  keywords: string[]
  strategy: number
  type: ObjectType
  enableIteration?: number
  description?: string
}

type UpdateParams = {
  name?: string
  keywords?: string[]
  strategy?: number
  chunkSize?: number
  description?: string
  candidateTrainSet?: number
  trainSetVersion?: number
  miningSet?: number
  testSet?: number
  modelStage?: number[]
  enableIteration?: number
  testingSets?: number[]
}

/** project service */
/**
 * @description get project detail
 * @export
 * @param {number} id
 * @return
 */
export function getProject(id: number) {
  return request.get(`projects/${id}`)
}

/**
 * @param {*} params
 * { name, offset = 0, limit = 10 }
 * @returns
 */
export function getProjects({ name, type, offset = 0, limit = 0 }: QueryParams) {
  return request.get('projects/', { params: { name, object_type: type, offset, limit } })
}

/**
 * delete project
 * @param {number} id
 * @returns
 */
export function delProject(id: number) {
  return request({
    method: 'delete',
    url: `/projects/${id}`,
  })
}

/**
 * create a project
 * @param {object} project
 * {
 *   {string}  name
 *   {string}  [description]
 *   {number}  [target_iteration]
 *   {number}  [target_map]
 *   {number}  [target_dataset]
 *   {array<string>}  keywords
 *   {boolean} enableIteration
 * }
 * @returns
 */
export function createProject({ name, description, type, keywords, strategy = 1, enableIteration }: CreateParams) {
  return request.post('/projects/', {
    name,
    description,
    object_type: type,
    training_keywords: keywords,
    mining_strategy: strategy,
    enable_iteration: enableIteration,
  })
}

/**
 * create an example project
 * @returns
 */
export function addExampleProject() {
  return request.post('/projects/samples')
}

/**
 * update project
 * @param {number} id
 * @param {object} params
 * {
 * {string} name
 * {number} strategy
 * {number} chunkSize
 * {string} description
 * {number} trainSetVersion
 * {number} miningSet
 * {number} testSet
 * {number} [modelStage]
 * {boolean} enableIteration
 * {array<number>} [testingSets]
 * }
 * @returns
 */
export function updateProject(id: number, project: UpdateParams) {
  const {
    name,
    keywords,
    strategy,
    chunkSize,
    description,
    candidateTrainSet,
    trainSetVersion,
    miningSet,
    testSet,
    modelStage = [],
    enableIteration,
    testingSets,
  } = project
  const [model, stage] = modelStage
  return request({
    method: 'patch',
    url: `/projects/${id}`,
    data: {
      name,
      training_keywords: keywords,
      mining_strategy: strategy,
      chunk_size: chunkSize,
      mining_dataset_id: miningSet,
      validation_dataset_id: testSet,
      description,
      initial_model_id: model,
      initial_model_stage_id: stage,
      initial_training_dataset_id: trainSetVersion,
      candidate_training_dataset_id: candidateTrainSet,
      enable_iteration: enableIteration,
      testing_dataset_ids: testingSets ? testingSets?.toString() : undefined,
    },
  })
}

/**
 * get project status, dirty/clean
 * @param {number} id
 * @returns
 */
export function checkStatus(id: number) {
  return request.get(`/projects/${id}/status`)
}
