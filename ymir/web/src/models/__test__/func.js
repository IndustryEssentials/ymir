import { put, call, select } from "redux-saga/effects"

export function errorCode(module, func, expected = null) {
  it(`effects: ${func} -> error code`, () => {
    const saga = module.effects[func]
    const id = 10024
    const creator = {
      type: func,
      payload: id,
    }
    const error = saga(creator, { put, call, select})
    error.next()
    const errorEnd = error.next({
      code: 11002,
      result: null,
    })

    if (expected) {
      expect(errorEnd.value).toEqual(expected)
    } else {
      expect(errorEnd.value).toBeUndefined()
    }
    expect(errorEnd.done).toBe(true)
  })
}