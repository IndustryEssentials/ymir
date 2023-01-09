import {
  getTensorboardLink,
} from '../common'

describe('service: common', () => {
  it('common:getTensorboardLink', () => {
    const path = '/tensorboard/#scalars&regexInput='
    const hash = 't23412352134215312342'

    expect(getTensorboardLink(hash)).toBe(path + hash)
    expect(getTensorboardLink()).toBe(path)
    expect(getTensorboardLink(null)).toBe(path)
  })
})