import { TYPES } from "../image"
import {
  getImageTypes,
 } from "../query"

function match (list, key, value) {
  const item = list.find(it => it.key === key)
  expect(item.value).toBe(value)
}

describe("constants: query", () => {
  it("have right image types", () => {
    const types = getImageTypes()
    match(types, 'all', undefined)
    match(types, 'train', TYPES.TRAINING)
    match(types, 'mining', TYPES.MINING)
  })
})
