import { TYPES } from "../image"
import { 
  getTaskTypes,
  getTaskStates,
  getTimes,
  getModelImportTypes,
  getDatasetTypes,
  getImageTypes,
 } from "../query"
import { TASKSTATES, TASKTYPES } from '../task'
jest.mock('@/utils/t', () => {
  return jest.fn()
})

function match (list, key, value) {
  const item = list.find(it => it.key === key)
  expect(item.value).toBe(value)
}

describe("constants: query", () => {
  it("have right task types", () => {
    const taskTypes = getTaskTypes()
    match(taskTypes, 'all', "")
    match(taskTypes, 'train', TASKTYPES.TRAINING)
    match(taskTypes, 'mining', TASKTYPES.MINING)
    match(taskTypes, 'label', TASKTYPES.LABEL)
    match(taskTypes, 'filter', TASKTYPES.FILTER)
  })
  it("have right task states", () => {
    const states = getTaskStates()
    match(states, 'all', "")
    match(states, 'pending', TASKSTATES.PENDING)
    match(states, 'doing', TASKSTATES.DOING)
    match(states, 'finish', TASKSTATES.FINISH)
    match(states, 'failure', TASKSTATES.FAILURE)
  })
  it("have right query periods", () => {
    const times = getTimes()
    expect(times[0].value).toBe(0)
    expect(times[1].value).toBe(1)
    expect(times[2].value).toBe(3)
    expect(times[3].value).toBe(7)
    expect(times[4].value).toBe(365)
  })
  it("have right model import type", () => {
    const types = getModelImportTypes()
    match(types, 'all', "")
    match(types, 'train', 1)
  })
  it("have right dataset types", () => {
    const types = getDatasetTypes()
    match(types, 'all', "")
    match(types, 'mining', 2)
    match(types, 'label', 3)
    match(types, 'filter', 4)
    match(types, 'import', 5)
  })
  it("have right image types", () => {
    const types = getImageTypes()
    match(types, 'all', undefined)
    match(types, 'train', TYPES.TRAINING)
    match(types, 'mining', TYPES.MINING)
  })
})
