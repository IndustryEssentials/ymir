import { generateName, templateString } from "../string"

describe("utils: number", () => {
  
  it('function: generateName. ', () => {
    const maps = [
      {expected: '', },
      {expected: 'datas', prefix: 'dataset_test_more', len: 12 },
      {expected: 'd', prefix: 'datasets', len: 8 },
      {expected: 'dataset', prefix: 'dataset', len: 0 },
      {expected: 'dataset', prefix: 'dataset' },
      {expected: 'datasetss', prefix: 'datasetss', len: 20 },
    ]
    maps.forEach(({ prefix, len, expected }) => expect(generateName(prefix, len).replace(/_\d+$/, '')).toBe(expected))
  })
  it('function: templateString. ', () => {
    const str = 'test {unit} {test2} {test3} about string template'
    const values = {
      unit: 'unit',
      test2: null,
    }
    const expected = 'test unit   about string template'
    expect(templateString(str, values)).toBe(expected)

    const none = 'it is a {test} test'
    const expected2 = 'it is a  test'
    expect(templateString(none)).toBe(expected2)
  })
})
