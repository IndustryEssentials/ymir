import {
  Stages,
  getStageLabel,
  StageList,
  transferIteration,
} from '../iteration'

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
  it("function -> transferIteration.", () => {
    const origin = {
      "iteration_round": 1,
      "previous_iteration": 0,
      "description": null,
      current_step: {
        id: 34
      },
      steps: [],
      "current_stage": 1,
      "mining_dataset_id": 20,
      "mining_input_dataset_id": 39,
      "mining_output_dataset_id": null,
      "label_output_dataset_id": null,
      "training_input_dataset_id": null,
      "training_output_model_id": null,
      "validation_dataset_id": null,
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
      currentStep: {
        finished: undefined,
        id: 34,
        name: undefined,
        percent: undefined,
        presetting: undefined,
        state: undefined,
        taskId: undefined,
        taskType: undefined,
      },
      steps: [],
      currentStage: 1,
      wholeMiningSet: 20,
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
