import { createFd } from "../transfer"

describe("utils: transfer", () => {
  it("transfer an object to a form data object", () => {
    const data = {
      id: "test",
      num: 0,
      arr: [1, 2, 3],
    }

    const formData = createFd(data)
    expect(formData.get("id")).toBe("test")
    expect(formData.get("num")).toBe("0")
    expect(formData.get("arr")).toBe(data.arr.toString())
  })
})
