import { getSetStates } from "../column"
import { TASKSTATES } from '../task'

jest.mock('@/utils/t', () => {
  return jest.fn()
})

describe("constants: column", () => {
  it("have right task states map", () => {
    const states = getSetStates()
    expect(states.find(state => state.key === 'pending').value).toBe(TASKSTATES.PENDING)
    expect(states.find(state => state.key === 'doing').value).toBe(TASKSTATES.DOING)
    expect(states.find(state => state.key === 'finish').value).toBe(TASKSTATES.FINISH)
    expect(states.find(state => state.key === 'failure').value).toBe(TASKSTATES.FAILURE)
  })
})
