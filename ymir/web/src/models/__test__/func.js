import { put, call, select, putResolve } from "redux-saga/effects"

put.resolve = putResolve

export function errorCode(module, func, payload = 10024, expected = null) {
  it(`effects: ${func} -> error code`, () => {
    const saga = module.effects[func]
    const creator = {
      type: func,
      payload,
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

export function normalReducer(module, func, payload, expected, field, initState) {
  it(`reducers: ${func}`, () => {
    const action = {
      payload,
    }
    const result = module.reducers[func]({[field]: initState}, action)
    expect(result[field]).toEqual(expected)
  })
}

export const product = (id) => ({ id })
export const products = (n) => Array.from({ length: n }, (item, index) => product(index + 1))
export const list = items => ({ items, total: items.length })
export const response = (result, code = 0) => ({ code, result })

export const generatorCreator = (module) => (func, payload) => {
  const saga = module['effects'][func]
  const creator = {
    type: func,
    payload,
  }

  return saga(creator, { put, call, select })
}
