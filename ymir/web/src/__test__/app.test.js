import { dva, onRouteChange } from "../app"
// import { location } from "umi"

const consoleSpy = jest.spyOn(console, "error").mockImplementation(() => {})

describe("app config", () => {
  it("dva config", () => {
    // on error
    const err = new ErrorEvent("it is a message for figure out error.")
    dva.config.onError(err)
    expect(consoleSpy).toHaveBeenCalled()
  })
})
