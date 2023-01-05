import { format } from '@/utils/date'
import { PROJECTTYPES, transferProject } from '../project'

jest.mock('umi', () => {
  return {
    getLocale() {
      return 'zh-CN'
    },
  }
})

const createTime = '2022-03-10T03:39:09'

describe('constants: project', () => {
  it('function -> transferProject.', () => {
    const origin = {
      name: 'project002',
      description: 'project002 desc',
      mining_strategy: 0,
      chunk_size: 0,
      object_type: PROJECTTYPES.ObjectDetection,
      iteration_target: null,
      map_target: 88,
      training_dataset_count_target: null,
      is_deleted: false,
      create_datetime: createTime,
      update_datetime: createTime,
      id: 1,
      training_dataset_group_id: 1,
      mining_dataset_id: null,
      validation_dataset_id: null,
      initial_model_id: null,
      initial_training_dataset_id: 1,
      current_iteration: null,
      training_dataset_group: {
        name: 'project002_training_dataset',
        project_id: 1,
        user_id: 3,
        description: null,
        is_deleted: false,
        create_datetime: createTime,
        update_datetime: createTime,
        id: 1,
      },
      validation_dataset: null,
      mining_dataset: null,
      testing_datasets: [],
      dataset_count: 6,
      model_count: 0,
      training_keywords: ['cat', 'person'],
      current_iteration_id: null,
      enable_iteration: true,
      total_asset_count: 0,
      running_task_count: 0,
      total_task_count: 0,
    }

    const expected = {
      id: 1,
      name: 'project002',
      keywords: ['cat', 'person'],
      trainSet: {
        id: 1,
        projectId: 1,
        name: 'project002_training_dataset',
        createTime: format(createTime),
        versions: [],
      },
      trainSetVersion: 1,
      testSet: undefined,
      miningSet: undefined,
      testingSets: [],
      setCount: 6,
      model: 0,
      modelStage: undefined,
      modelCount: 0,
      miningStrategy: 0,
      chunkSize: 0,
      currentIteration: undefined,
      currentStep: '',
      round: 0,
      hiddenDatasets: [],
      hiddenModels: [],
      createTime: format(createTime),
      description: 'project002 desc',
      type: PROJECTTYPES.ObjectDetection,
      typeLabel: "project.types.det",
      isExample: false,
      updateTime: format(createTime),
      enableIteration: true,
      totalAssetCount: 0,
      candidateTrainSet: 0,
      datasetCount: 6,
      datasetProcessingCount: 0,
      datasetErrorCount: 0,
      modelCount: 0,
      modelProcessingCount: 0,
      modelErrorCount: 0,
    }
    expect(transferProject(origin)).toEqual(expected)
  })
})
