import {
  getTasks,
  getTask,
  deleteTask,
  updateTask,
  createFilterTask,
  createLabelTask,
  createTrainTask,
  createMiningTask,
  createTask,
} from "../task"
import request from '@/utils/request'

jest.mock('@/utils/request', () => {
  const req = jest.fn()
  req.get = jest.fn()
  req.post = jest.fn()
  return req
})

describe("service: tasks", () => {
  it("getTasks -> success", () => {
    const params = {
      name: 'testname',
      type: 1,
      state: 1,
      start_time: 123942134,
      end_time: 134123434,
      offset: 0,
      limit: 20,
    }
    const expected = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    request.get.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: {
          items: expected,
          total: expected.length,
        },
      })
    })

    getTasks(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.items).toEqual(expected)
      expect(result.total).toBe(expected.length)
    })
  })
  it("getTask -> success", () => {
    const id = 613
    const expected = {
      id,
      name: '60taskname',
    }
    request.get.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: expected,
      })
    })

    getTask(id).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.id).toBe(id)
      expect(result.name).toBe(expected.name)
    })
  })

  it("createFilterTask -> success", () => {
    const params = {
      name: 'taskname',
      datasets: [34, 56, 348],
      include: ['k1', 'k2'],
      exclude: ['k3']
    }
    const expected = { id: 612 }
    request.post.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: expected,
      })
    })

    createFilterTask(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.id).toBe(expected.id)
    })
  })

  it("createTrainTask -> success", () => {
    const params = {
      name: 'taskname',
      train_sets: [1, 3, 4],
      validation_sets: [5],
      backbone: 'darknet',
      hyperparameter: 'epco v10',
      network: 'YOLO v4',
      keywords: ['cat', 'dog'],
      train_type: 1,
    }
    const expected = { id: 611 }
    request.post.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: expected,
      })
    })

    createTrainTask(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.id).toBe(expected.id)
    })
  })
  it("createMiningTask -> success", () => {
    const params = {
      model: 'modelhash',
      topk: 1000,
      datasets: [1, 2],
      exclude_sets: [],
      algorithm: 'LYDD',
      name: 'taskname',
    }
    const expected = { id: 610 }
    request.post.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: expected,
      })
    })

    createMiningTask(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.id).toBe(expected.id)
    })
  })
  it("createLabelTask -> success", () => {
    const params = {
      name: 'taskname',
      datasets: [23, 34],
      label_members: ['a@test.com', 'b@test.com'],
      keywords: ['cat', 'dog'],
      doc: 'http://test.com/test.pdf'
    }
    const expected = { id: 609 }
    request.post.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: expected,
      })
    })

    createLabelTask(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.id).toBe(expected.id)
    })
  })
  it("deleteTask -> success", () => {
    const id = 608
    const expected = "ok"
    request.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: expected,
      })
    })

    deleteTask(id).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result).toBe(expected)
    })
  })
  it("updateTask -> success", () => {
    const id = 607
    const name = 'newnameoftask'
    const expected = { id, name }
    request.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: expected,
      })
    })

    updateTask(id, name).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result.id).toEqual(id)
      expect(result.name).toEqual(name)
    })
  })
  it("createTask -> success", () => {
    const params = {
      name: 'newtask',
    }
    const expected = "ok"
    request.post.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: expected,
      })
    })

    createTask(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result).toBe(expected)
    })
  })
})
