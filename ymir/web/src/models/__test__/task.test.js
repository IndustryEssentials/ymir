import task from '../task'
import { put, putResolve, call, select } from 'redux-saga/effects'
import { errorCode } from './func'

put.resolve = putResolve

describe('models: task', () => {
  const product = (id) => ({ id })
  const products = (n) => Array.from({ length: n }, (item, index) => product(index + 1))
  errorCode(task, 'fusion')
  errorCode(task, 'merge')
  errorCode(task, 'filter')
  errorCode(task, 'train')
  errorCode(task, 'mine')
  errorCode(task, 'stopTask')

  it('effects: fusion', () => {
    const saga = task.effects.fusion
    const creator = {
      type: 'fusion',
      payload: {},
    }
    const expected = 'ok'

    const generator = saga(creator, { put, call })
    const start = generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    expect(end.value).toBe(expected)
    expect(end.done).toBe(true)
  })

  it('effects: merge', () => {
    const saga = task.effects.merge
    const creator = {
      type: 'merge',
      payload: {},
    }
    const expected = 'ok'

    const generator = saga(creator, { put, call })
    const start = generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    expect(end.value).toBe(expected)
    expect(end.done).toBe(true)
  })

  it('effects: filter', () => {
    const saga = task.effects.filter
    const creator = {
      type: 'filter',
      payload: {},
    }
    const expected = 'ok'

    const generator = saga(creator, { put, call })
    const start = generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    expect(end.value).toBe(expected)
    expect(end.done).toBe(true)
  })

  it('effects: train', () => {
    const saga = task.effects.train
    const creator = {
      type: 'train',
      payload: {},
    }
    const expected = 'ok'

    const generator = saga(creator, { put, putResolve, call })
    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    const end = generator.next()

    expect(end.value).toBe(expected)
    expect(end.done).toBe(true)
  })
  it('effects: mine', () => {
    const saga = task.effects.mine
    const creator = {
      type: 'mine',
      payload: {},
    }
    const expected = 'ok'

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    const end = generator.next()

    expect(end.value).toBe(expected)
    expect(end.done).toBe(true)
  })

  it('effects: label', () => {
    const saga = task.effects.label
    const creator = {
      type: 'label',
      payload: { keywords: ['person', 'dog'] },
    }
    const expected = 'ok'

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })

    const end = generator.next()

    expect(end.value).toBe(expected)
    expect(end.done).toBe(true)
  })

  it('effects: stopTask', () => {
    const saga = task.effects.stopTask
    const id = 235
    const creator = {
      type: 'stopTask',
      payload: id,
    }
    const expected = { id }

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    generator.next()
    const end = generator.next()

    expect(end.value.id).toBe(id)
    expect(end.done).toBe(true)
  })

  it('effects: stopTask -> success', () => {
    const saga = task.effects.stopTask
    const id = 236
    const creator = {
      type: 'stopTask',
      payload: { id },
    }
    const expected = { id }

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    generator.next()
    const end = generator.next()

    expect(end.value.id).toBe(id)
    expect(end.done).toBe(true)
  })
  it('effects: stopTask - no result', () => {
    const saga = task.effects.stopTask
    const id = 236
    const creator = {
      type: 'stopTask',
      payload: { id, with_data: true },
    }

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 4002,
      result: null,
    })

    expect(end.value).toBeUndefined()
    expect(end.done).toBe(true)
  })
})
