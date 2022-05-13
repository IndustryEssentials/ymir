import iteration from "../iteration"
import { put, putResolve, call, select } from "redux-saga/effects"
import { errorCode, normalReducer } from "./func"
import { Stages, transferIteration } from '@/constants/project'

put.resolve = putResolve

function equalObject(obj1, obj2) {
  expect(JSON.stringify(obj1)).toBe(JSON.stringify(obj2))
}

describe("models: iteration", () => {
  const product = (id) => ({ id })
  const products = (n) =>
    Array.from({ length: n }, (item, index) => product(index + 1))
  normalReducer(iteration, 'UPDATE_ITERATIONS', { id: 13424, iterations: product(34) }, { 13424: product(34) }, 'iterations', {})
  normalReducer(iteration, 'UPDATE_ITERATION', product(100434), product(100434), 'iteration', {})
  normalReducer(iteration, 'UPDATE_CURRENT_STAGE_RESULT', product(100435), product(100435), 'currentStageResult', {})

  errorCode(iteration, "getIterations")
  errorCode(iteration, "getIteration")
  errorCode(iteration, "createIteration")
  errorCode(iteration, "updateIteration")

  it("effects: getIterations -> success", () => {
    const saga = iteration.effects.getIterations
    const creator = {
      type: "getIterations",
      payload: {},
    }
    const iterations = products(5)
    const expected = iterations.map(i => transferIteration(i))

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: iterations,
    })
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: getIterations -> success -> get more info with data.", () => {
    const saga = iteration.effects.getIterations
    const pid = 64321
    const creator = {
      type: "getIterations",
      payload: { id: pid, more: true },
    }
    const iterations = products(3).map(({ id }) => ({
      id,
      mining_input_dataset_id: id,
      mining_output_dataset_id: id,
      label_output_dataset_id: id,
      training_input_dataset_id: id,
      training_output_model_id: id,
      testing_dataset_id: id,
    }))
    const datasets = products(3)
    const models = products(3)
    const expected = iterations.map(i => ({
      ...transferIteration(i),
      trainUpdateDataset: product(i.id),
      miningDataset: product(i.id),
      miningResultDataset: product(i.id),
      labelDataset: product(i.id),
      trainingModel: product(i.id),
      testDataset: product(i.id),
    }))

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: iterations,
    })
    generator.next(datasets)
    generator.next(models)
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })

  it("effects: getIteration", () => {
    const saga = iteration.effects.getIteration
    const id = 10012
    const pid = 62314
    const creator = {
      type: "getIteration",
      payload: { pid, id },
    }
    const result = { id, project_id: pid, name: "iteration001" }
    const expected = transferIteration(result)

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result,
    })
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: getStageResult", () => {
    const saga = iteration.effects.getStageResult
    const stage = 1
    const pid = 62314
    const creator = {
      type: "getStageResult",
      payload: { id: pid, stage, },
    }
    const result = { id: 254, project_id: pid, name: "iteration002" }
    const expected = result

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next(result)
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: getStageResult -> get model", () => {
    const saga = iteration.effects.getStageResult
    const stage = Stages.training
    const pid = 62314
    const creator = {
      type: "getStageResult",
      payload: { id: pid, stage, force: true },
    }
    const result = product(2345)
    const expected = result

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next(result)
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: updateCurrentStageResult -> progress", () => {
    const saga = iteration.effects.updateCurrentStageResult
    const ds = (id, state, result_state, progress) => ({
      id,
      task: { hash: `hash${id}`, state, percent: progress, },
      taskState: state,
      state: result_state, progress
    })

    const result = ds(1, 2, 0, 0.20)
    const task1 = { hash1: { id: 1, state: 2, result_state: 0, percent: 0.45 }, hash7: { id: 7, state: 3, result_state: 1, percent: 1 } }
    const creator = {
      type: "updateDatasets",
      payload: task1,
    }
    const expected = ds(1, 2, 0, 0.45)

    const generator = saga(creator, { put, call, select })
    generator.next()
    const d = generator.next(result)
    const end = generator.next()
    const updated = d.value.payload.action.payload

    expect(updated).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: updateCurrentStageResult -> state change.", () => {
    const saga = iteration.effects.updateCurrentStageResult
    const ds = (id, state, result_state, progress) => ({
      id,
      task: { hash: `hash${id}`, state, percent: progress, },
      taskState: state,
      state: result_state, progress
    })

    const result = ds(1, 2, 0, 0.20)
    const task = { hash1: { id: 1, state: 3, result_state: 1, percent: 1 } }
    const creator = {
      type: "updateDatasets",
      payload: task,
    }
    const expected = { ...ds(1, 3, 1, 1), needReload: true }

    const generator = saga(creator, { put, call, select })
    generator.next()
    const d = generator.next(result)
    const end = generator.next()
    const updated = d.value.payload.action.payload

    expect(updated).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: createIteration", () => {
    const saga = iteration.effects.createIteration
    const id = 10015
    const expected = { id, name: "new_iteration_name" }
    const creator = {
      type: "createIteration",
      payload: { name: "new_iteration_name", type: 1 },
    }

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    equalObject(expected, end.value)
    expect(end.done).toBe(true)
  })
  it("effects: updateIteration", () => {
    const saga = iteration.effects.updateIteration
    const origin = { id: 10011, name: "new_iteration_name" }
    const creator = {
      type: "updateIteration",
      payload: { ...origin },
    }
    const expected = transferIteration(origin)

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })

  it("effects: getIterationStagesResult -> get model", () => {
    const saga = iteration.effects.getIterationStagesResult

    const pid = 62314
    const iter = {
      id: 5349,
      projectId: pid,
      miningSet: 5340,
      miningResult: 5341,
      labelSet: 5342,
      trainUpdateSet: 5343,
      model: 34234,
    }
    const datasets = [product(5340), product(5341), product(5342), product(5343)]
    const model = product(32234)
    const creator = {
      type: "getIterationStagesResult",
      payload: iter,
    }
    const expected = {
      ...iter,
      iminingSet: product(5340),
      iminingResult: product(5341),
      ilabelSet: product(5342),
      itrainUpdateSet: product(5343),
      imodel: product(32234),
    }

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next(datasets)
    const end = generator.next(model)

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
})
