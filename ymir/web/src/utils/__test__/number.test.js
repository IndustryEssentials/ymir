import { humanize, randomBetween, randomNumber, } from "../number"

describe("utils: number", () => {
  it("function: humanize. humanize number.", () => {
    const numbers = [
      {value: 324, expected: '324' },
      {value: 3324, expected: '3K' },
      {value: 395324, expected: '395K' },
      {value: 12395324, expected: '12M' },
      {value: 2425435324, expected: '2B' },
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
})
