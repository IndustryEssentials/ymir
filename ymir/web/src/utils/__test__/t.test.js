jest.mock('umi', () => {
  const intl = () => {
    return {
      formatMessage: jest.fn(({ id }, values) => {
        return { id, values, type: 'text' }
      }),
      formatHTMLMessage: jest.fn(({ id }, values) => {
        return { id, values, type: 'html' }
      }),
    }
  }
  return {
    useIntl: intl,
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
      expect(normal.type).toBe('text')

      const withValues = t(id, values)
      expect(withValues.id).toBe(id)
      expect(withValues.values.name).toBe(name)
    })

  })
  it("formatHtml: language transfer", () => {
    jest.isolateModules(() => {
      const formatHtml = require('../t').formatHtml
      const id = 'target4332453'
      const name = 'world'
      const values = { name }

      const normal = formatHtml(id)
      expect(normal.id).toBe(id)
      expect(normal.type).toBe('html')

      const withValues = formatHtml(id, values)
      expect(withValues.id).toBe(id)
      expect(withValues.values.name).toBe(name)
    })
  })
})
