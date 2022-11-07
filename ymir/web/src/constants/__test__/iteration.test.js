import {
  Stages,
  getStepLabel,
  StageList,
  transferIteration,
  STEP,
  getSteps,
} from "../iteration"

jest.mock("umi", () => {
  return {
    getLocale() {
      return "zh-CN"
    },
  }
})

const createTime = "2022-03-10T03:39:09"

describe("constants: project", () => {
  it("function -> getStepLabel.", () => {
    expect(getStepLabel(STEP.prepareMining, 1)).toBe(
      "project.iteration.stage.ready"
    )
    expect(getStepLabel(STEP.mining, 1)).toBe("project.iteration.stage.mining")
    expect(getStepLabel(STEP.labelling, 1)).toBe(
      "project.iteration.stage.label"
    )
    expect(getStepLabel(STEP.merging, 1)).toBe("project.iteration.stage.merge")
    expect(getStepLabel(STEP.training, 1)).toBe(
      "project.iteration.stage.training"
    )
    expect(getStepLabel(STEP.next, 1)).toBe("project.iteration.stage.next")
    expect(getStepLabel(STEP.next)).toBe("project.iteration.stage.prepare")
    expect(getStepLabel(STEP.next, 0)).toBe("project.iteration.stage.prepare")
  })
  it("function -> getSteps.", () => {
    const steps = getSteps()

    expect(steps).toBeInstanceOf(Array)
    expect(steps.length).toBe(6)

    steps.forEach((step) => {
      expect(step).toBeInstanceOf(Object)
      expect(step.value).toBeDefined()
      expect(step.label).toBeDefined()
    })
  })
  it("function -> transferIteration.", () => {
    const origin = {
      iteration_round: 1,
      previous_iteration: 0,
      description: null,
      current_step: {
        id: 34,
      },
      steps: [],
      current_stage: 1,
      mining_dataset_id: 20,
      mining_input_dataset_id: 39,
      mining_output_dataset_id: null,
      label_output_dataset_id: null,
      training_input_dataset_id: null,
      training_output_model_id: null,
      validation_dataset_id: null,
      user_id: 2,
      project_id: 8,
      is_deleted: false,
      create_datetime: "2022-04-13T10:03:49",
      update_datetime: "2022-04-13T10:04:02",
      id: 3,
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
      prevIteration: 0,
    }
    expect(transferIteration(origin)).toEqual(expected)
  })
})
