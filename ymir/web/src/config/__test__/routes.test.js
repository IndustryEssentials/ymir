import routes from "../routes"

const check = (routes) => {
  routes.forEach((route) => {
    expect(route).toHaveProperty("path", expect.any(String))
    if (!route.redirect) {
      expect(route).toHaveProperty("component", expect.any(String))
    }
    if (route.routes) {
      check(route.routes)
    }
  })
}

describe("config: routes", () => {
  it("return an array that have the same former in deep", () => {
    check(routes)
  })
})
