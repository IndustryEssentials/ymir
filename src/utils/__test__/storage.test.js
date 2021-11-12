import storage from "../storage"

describe("utils: storage", () => {
  const value = "str"
  const key = "test"
  it("set and value", () => {
    storage.set(key, value)
    expect(localStorage.getItem(key)).toBe(JSON.stringify(value))
  })

  it("get value", () => {
    expect(storage.get("test")).toBe(value)
  })

  it("remove value", () => {
    storage.remove(key)
    // expect(storage.remove(key)).toBe(true)
    expect(storage.get(key)).toBe(null)
  })
})
