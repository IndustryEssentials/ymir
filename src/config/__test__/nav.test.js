import navs from "../nav"
import t from '@/utils/t'

jest.mock('@/utils/t')
t.mockReturnValue('')
const check = (navs) => {
  navs.forEach((nav) => {
    expect(nav).toHaveProperty("key", expect.any(String))
    expect(nav).toHaveProperty("label", expect.any(String))
    if (nav.sub) {
      check(nav.sub)
    }
  })
}

describe("config: nav", () => {
  it("return an array that have the same former in deep", () => {
    check(navs())
  })
})
