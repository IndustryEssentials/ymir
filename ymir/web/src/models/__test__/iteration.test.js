import iteration from "../iteration"
import { put, putResolve, call, select } from "redux-saga/effects"
import { product, products, errorCode, normalReducer, generatorCreator } from "./func"
import { Stages, transferIteration } from '@/constants/iteration'

put.resolve = putResolve

function equalObject(obj1, obj2) {
  expect(JSON.stringify(obj1)).toBe(JSON.stringify(obj2))
}

describe("models: iteration", () => {
  const createGenerator = generatorCreator(iteration)
  normalReducer(iteration, 'UPDATE_ITERATIONS', { id: 13424, iterations: product(34) }, { 13424: product(34) }, 'iterations', {})
  normalReducer(iteration, 'UPDATE_ITERATION', product(100434), { 100434: product(100434) }, 'iteration', {})
  normalReducer(iteration, 'UPDATE_CURRENT_STAGE_RESULT', product(100435), product(100435), 'currentStageResult', {})

  errorCode(iteration, "getIterations")
  errorCode(iteration, "getIteration")
  errorCode(iteration, "createIteration")
  errorCode(iteration, "updateIteration")

  it("effects: getIterations -> success", () => {
    const iterations = products(5)
    const expected = iterations.map(i => transferIteration(i))

    const generator = createGenerator('getIterations', {})
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
    const pid = 64321
    const iterations = products(3).map(({ id }) => ({
      id,
      mining_dataset_id: id,
      mining_input_dataset_id: id,
      mining_output_dataset_id: id,
      label_output_dataset_id: id,
      training_input_dataset_id: id,
      training_output_model_id: id,
      validation_dataset_id: id,
    }))
    const datasets = products(3)
    const models = products(3)
    const expected = iterations.map(i => ({
      ...transferIteration(i),
      entities: {
        wholeMiningSet: product(i.id),
        trainUpdateSet: product(i.id),
        miningSet: product(i.id),
        miningResult: product(i.id),
        labelSet: product(i.id),
        testSet: product(i.id),
        model: product(i.id),
      }
    }))

    const generator = createGenerator('getIterations', { id: pid, more: true })
    generator.next()
    generator.next({
      code: 0,
      result: iterations,
    })
    generator.next(expected)
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })

  it("effects: getIteration", () => {
    const id = 10012
    const pid = 62314
    const result = { id, project_id: pid, name: "iteration001" }
    const expected = transferIteration(result)

    const generator = createGenerator('getIteration', { pid, id })
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
    const stage = 1
    const pid = 62314
    const result = { id: 254, project_id: pid, name: "iteration002" }
    const expected = result

    const generator = createGenerator('getStageResult', { id: pid, stage, })
    generator.next()
    generator.next(result)
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: getStageResult -> get model", () => {
    const stage = Stages.training
    const pid = 62314
    const result = product(2345)
    const expected = result

    const generator = createGenerator('getStageResult', { id: pid, stage, force: true })
    generator.next()
    generator.next(result)
    const end = generator.next()

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it("effects: createIteration", () => {
    const id = 10015
    const expected = { id, name: "new_iteration_name" }


    const generator = createGenerator('createIteration', { name: "new_iteration_name", type: 1 })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    equalObject(expected, end.value)
    expect(end.done).toBe(true)
  })
  it("effects: updateIteration", () => {
    const origin = { id: 10011, name: "new_iteration_name" }

    const expected = transferIteration(origin)
    const generator = createGenerator('updateIteration', origin)

    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    expect(end.value).toEqual(expected)
    expect(end.done).toBe(true)
  })
  it('effects: setCurrentStageResult -> success', () => {
    const model = product(523464)
    const expected = model
    const generator = createGenerator('setCurrentStageResult', model)
    generator.next()
    const end = generator.next()
    expect(end.value).toEqual(expected)
  })
})
