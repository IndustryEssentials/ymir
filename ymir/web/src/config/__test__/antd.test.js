import { formLayout, tailLayout, layout420 } from "../antd"

describe("config: antd", () => {
  it("formLayout", () => {
    expect(formLayout.labelCol.span).toBe(6)
    expect(formLayout.wrapperCol.span).toBe(16)
  })
  it("tailLayout", () => {
    expect(tailLayout.wrapperCol.offset).toBe(6)
    expect(tailLayout.wrapperCol.span).toBe(18)
  })
  it("layout420", () => {
    expect(layout420.labelCol.span).toBe(4)
    expect(layout420.wrapperCol.span).toBe(20)
  })
})
