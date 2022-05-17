import { format } from '@/utils/date'
import {
  Stages,
  getStageLabel,
  StageList,
  getIterationVersion,
  transferProject,
  transferIteration,
} from '../project'

jest.mock('umi', () => {
  return {
    getLocale() {
      return 'zh-CN'
    },
  }
})

const createTime = "2022-03-10T03:39:09"

describe("constants: project", () => {
  it("function -> getStageLabel.", () => {
    expect(getStageLabel(Stages.prepareMining, 1)).toBe('project.iteration.stage.ready')
    expect(getStageLabel(Stages.mining, 1)).toBe('project.iteration.stage.mining')
    expect(getStageLabel(Stages.labelling, 1)).toBe('project.iteration.stage.label')
    expect(getStageLabel(Stages.merging, 1)).toBe('project.iteration.stage.merge')
    expect(getStageLabel(Stages.training, 1)).toBe('project.iteration.stage.training')
    expect(getStageLabel(Stages.next, 1)).toBe('project.iteration.stage.next')
    expect(getStageLabel(Stages.next)).toBe('project.iteration.stage.prepare')
    expect(getStageLabel(Stages.next, 0)).toBe('project.iteration.stage.prepare')

  })
  it("function -> StageList.", () => {
    const stageList = StageList()

    expect(stageList.list).toBeInstanceOf(Array)
    expect(stageList.list.length).toBe(6)

    stageList.list.map(({ value }) => value).forEach(stage => {
      const stageObj = stageList[stage]
      expect(stageObj).toBeInstanceOf(Object)
      expect(stageObj.value).toBeDefined()
      expect(stageObj.label).toBeDefined()
    })

  })
  it("function -> getIterationVersion.", () => {
    expect(getIterationVersion(1)).toBe('V1')
  })
  it("function -> transferProject.", () => {
    const origin = {
      "name": "project002",
      "description": "project002 desc",
      "mining_strategy": 0,
      "chunk_size": 0,
      "training_type": 1,
      "iteration_target": null,
      "map_target": 88,
      "training_dataset_count_target": null,
      "is_deleted": false,
      "create_datetime": createTime,
      "update_datetime": createTime,
      "id": 1,
      "training_dataset_group_id": 1,
      "mining_dataset_id": null,
      "testing_dataset_id": null,
      "initial_model_id": null,
      "initial_training_dataset_id": 1,
      "current_iteration": null,
      "training_dataset_group": {
        "name": "project002_training_dataset",
        "project_id": 1,
        "user_id": 3,
        "description": null,
        "is_deleted": false,
        "create_datetime": createTime,
        "update_datetime": createTime,
        "id": 1,
      },
      "testing_dataset": null,
      "mining_dataset": null,
      "dataset_count": 6,
      "model_count": 0,
      "training_keywords": [
        "cat",
        "person"
      ],
      "current_iteration_id": null
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
      setCount: 6,
      model: 0,
      modelCount: 0,
      miningStrategy: 0,
      chunkSize: 0,
      currentIteration: undefined,
      currentStage: 0,
      round: 0,
      hiddenDatasets: [],
      hiddenModels: [],
      createTime: format(createTime),
      description: 'project002 desc',
      type: 1,
      isExample: false,
      updateTime: format(createTime)
    }
    expect(transferProject(origin)).toEqual(expected)

  })
  it("function -> transferIteration.", () => {
    const origin = {
      "iteration_round": 1,
      "previous_iteration": 0,
      "description": null,
      "current_stage": 1,
      "mining_input_dataset_id": 39,
      "mining_output_dataset_id": null,
      "label_output_dataset_id": null,
      "training_input_dataset_id": null,
      "training_output_model_id": null,
      "testing_dataset_id": null,
      "user_id": 2,
      "project_id": 8,
      "is_deleted": false,
      "create_datetime": "2022-04-13T10:03:49",
      "update_datetime": "2022-04-13T10:04:02",
      "id": 3
    }
    const expected = {
      id: 3,
      projectId: 8,
      name: undefined,
      round: 1,
      currentStage: 1,
      miningSet: 39,
      miningResult: null,
      labelSet: null,
      trainUpdateSet: null,
      model: null,
      trainSet: undefined,
      testSet: 0,
      prevIteration: 0
    }
    expect(transferIteration(origin)).toEqual(expected)

  })
})
