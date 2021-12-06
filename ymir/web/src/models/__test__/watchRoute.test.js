import watchRoute from "../watchRoute"
import { put, call } from "redux-saga/effects"

describe("models: watchRoute", () => {
  it("reducers: UPDATEROUTE", () => {
    const state = {
      current: "/",
    }
    const expected = "/tasks"
    const action = {
      payload: expected,
    }
    const { current } = watchRoute.reducers.UPDATEROUTE(state, action)
    expect(current).toBe(expected)
  })

  it("effects: updateRoute", () => {
    const saga = watchRoute.effects.updateRoute
    const creator = {
      type: "updateRoute",
      payload: {},
    }
    const expected = "/expected"
    const state = {
      payload: expected,
    }

    const generator = saga(creator, { put, call })
    generator.next(state)
    generator.next()
    const end = generator.next()

    expect(end.done).toBe(true)
  })
})
