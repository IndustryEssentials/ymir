import {
  getIterations,
  getIteration,
  createIteration,
  updateIteration,
} from "../iteration"
import { product, products, requestExample } from './func'

describe("service: iterations", () => {
  it("getIterations -> success", () => {
    const params = { name: 'testname', offset: 0, limit: 10 }
    const params2 = {}
    const expected = products(15)
    requestExample(getIterations, params, { items: expected, total: expected.length }, 'get')
    requestExample(getIterations, params2, { items: expected, total: expected.length })
  })
  it("getIteration -> success", () => {
    const id = 9623
    const expected = {
      id,
      name: '63iterationname',
    }
    requestExample(getIteration, id, expected, 'get')
  })
  it("updateIteration -> success", () => {
    const id = 9637
    const iteration = {
      description: 'memo',
      iteration_target: 10,
      keywords: ['cat', 'dog'],
      name: 'newporjectname',
      training_dataset_count_target: 0,
      type: 0,
    }
    const expected = { id, name }
    requestExample(updateIteration, [id, iteration], expected, 'post')
  })
  it("createIteration -> success", () => {
    const iteration = {
      description: 'memo',
      iteration_target: 10,
      keywords: ['cat', 'dog'],
      name: 'newporjectname',
      training_dataset_count_target: 0,
      type: 0,
    }
    const expected = "ok"
    requestExample(createIteration, iteration, expected, 'post')
  })
})
