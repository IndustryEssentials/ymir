import { humanize, isNumber, percent, randomBetween, randomNumber, toFixed, } from "../number"

describe("utils: number", () => {
  it("function: humanize. humanize number.", () => {
    const numbers = [
      { value: 324, expected: '324' },
      { value: 3324, expected: '3K' },
      { value: 395324, expected: '395K' },
      { value: 12395324, expected: '12M' },
      { value: 2425435324, expected: '2B' },
    ]
    numbers.forEach(num => expect(humanize(num.value)).toBe(num.expected))
    expect(humanize()).toBe(0)
    expect(humanize('243')).toBe('243')
    expect(humanize('43asdfj')).toBe('43asdfj')
  })
  it("function: randomNumber. generate random number", () => {
    const numbers = [1, 3, 5, 10]
    numbers.forEach(num => expect(String(randomNumber(num))).toMatch(new RegExp(`^\\d{${num}}$`)))
    expect(String(randomNumber())).toMatch(/^\d{6}$/)
  })
  it("function: randomBetween. generate number between [min and max)", () => {

    const normal = randomBetween(0, 6)
    expect(normal).toBeGreaterThanOrEqual(0)
    expect(normal).toBeLessThan(6)
    const excludeSituation = randomBetween(1, 3, 1)
    expect(excludeSituation).toBe(2)
  })
  it('function: toFixed. ', () => {
    const maps = [
      { expected: '12.43', value: 12.4346435, keep: 2 },
      { expected: '1.235',  value: 1.234564453, keep: 3 },
      { expected: '1.23',  value: 1.23456445312346234234, keep: 2 },
      { expected: '1235',  value: 1235 },
      { expected: '1.000',  value: 1, keep: 3 },
      { expected: '0.300',  value: 0.29999, keep: 3 },
      { expected: '1.34523d4',  value: '1.34523d4', keep: 2 },
    ]
    maps.forEach(({ expected, value, keep }) => expect(toFixed(value, keep)).toBe(expected))
  })
  it('function: percent. ', () => {
    const maps = [
      { expected: '12.43%', value: 0.124346435, keep: 2 },
      { expected: '23.5%',  value: 0.234564453, keep: 1 },
      { expected: '23.46%',  value: 0.23456445312346234234, keep: 2 },
      { expected: '100.00%',  value: 1 },
      { expected: '100.000%',  value: 1, keep: 3 },
      { expected: '23.4090%',  value: 0.23409, keep: 4 },
    ]
    maps.forEach(({ expected, value, keep }) => expect(percent(value, keep)).toBe(expected))
  })
  it('function: isNumber. ', () => {
    expect(isNumber()).toBe(false)
    expect(isNumber(null)).toBe(false)
    expect(isNumber(undefined)).toBe(false)
    expect(isNumber(isNaN)).toBe(false)
    expect(isNumber('134.3423')).toBe(false)
    expect(isNumber(true)).toBe(false)
    expect(isNumber(13e2)).toBe(true)
    expect(isNumber(1.34)).toBe(true)
  })
})
