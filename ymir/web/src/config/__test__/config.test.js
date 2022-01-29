import config from "../config"

describe("config: config", () => {
  it("return an object having define configuration", () => {
    expect(config).toHaveProperty("locale", expect.anything())
    expect(config).toHaveProperty("routes", expect.any(Array))
    expect(config).toHaveProperty("outputPath", "ymir")
    expect(config).toHaveProperty("hash", true)
    expect(config).toHaveProperty("nodeModulesTransform", expect.anything())
    expect(config).toHaveProperty("fastRefresh", expect.anything())
  })
})
