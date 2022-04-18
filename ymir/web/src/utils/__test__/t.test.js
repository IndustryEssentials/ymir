jest.mock('umi', () => {
  const intl = () => {
    return {
      formatMessage: jest.fn(({ id }, values) => {
        return { id, values }
      }),
    }
  }
  return {
    useIntl: intl,
    getLocale() {
      return 'en-US'
    },
  }
})
describe("utils: t", () => {
  it("t: language transfer", () => {
    jest.isolateModules(() => {
      const t = require('../t').default
      const id = 'target12379'
      const name = 'hello'
      const values = { name }

      const normal = t(id)
      expect(normal.id).toBe(id)

      const withValues = t(id, values)
      expect(withValues.id).toBe(id)
      expect(withValues.values.name).toBe(name)
    })

  })
})
