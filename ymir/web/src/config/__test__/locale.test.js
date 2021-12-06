import locale from "../locale"

describe("config: locale", () => {
  it("default language: en-US", () => {
    expect(locale.default).toBe("en-US")
  })

  it("locale for title: true", () => {
    expect(locale.title).toBe(true)
  })

  it("antd and base navigator have locale", () => {
    expect(locale.antd).toBe(true)
    expect(locale.baseNavigator).toBe(true)
  })

  it("base separator is -", () => {
    expect(locale.baseSeparator).toBe("-")
  })
})
