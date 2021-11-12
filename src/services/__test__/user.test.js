import { login, loginout, getMeInfo, signup, resetPwd, modifyPwd, forgetPwd } from "../Auth"
import request from '@/utils/request'

jest.mock('@/utils/request', () => {
  const req = jest.fn()
  req.get = jest.fn()
  req.post = jest.fn()
  return req
})

describe("service: auth", () => {
  it("login -> success", () => {
    const params = { username: "idol", password: "1q2w3e" }
    const expected = "token"
    request.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: {
          access_token: expected,
        },
      })
    })

    login(params).then(({ result }) => {
      expect(result.access_token).toBe(expected)
    })
  })
  it("loginout -> success", () => {
    const params = {}
    const expected = "ok"
    request.post.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: expected,
      })
    })

    loginout(params).then(({ result }) => {
      expect(result).toBe(expected)
    })
  })
  it("getMeInfo -> success", () => {
    const expected = {
      username: "president",
      email: "test@test.com",
      phone: "13245678908",
      id: 1345,
    }
    request.get.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: expected,
      })
    })

    getMeInfo().then(({ code, result }) => {
      expect(result).toEqual(expected)
    })
  })

  it('signup -> success', () => {
    const params = { username: "idol", password: "password", email: 'test@test.com' }
    const expected = { access_token: 'itisaaccesstoken' }
    request.post.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: expected,
      })
    })

    signup(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result).toEqual(expected)
    })
  })
  it('forgetPwd -> success', () => {
    
    const params = { email: 'test@test.com' }
    const expected = "ok"
    request.post.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: expected,
      })
    })

    forgetPwd(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result).toEqual(expected)
    })
  })
  it('modifyPwd -> success', () => {
    
    const params = { old: 'oldpassword', newPassword: 'newpassword' }
    const expected = "ok"
    request.post.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: expected,
      })
    })

    modifyPwd(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result).toEqual(expected)
    })
  })
  it('resetPwd -> success', () => {
    
    const params = { old: 'oldpassword', newPassword: 'newpassword' }
    const expected = "ok"
    request.post.mockImplementationOnce(() => {
      return Promise.resolve({
        code: 0,
        result: expected,
      })
    })

    resetPwd(params).then(({ code, result }) => {
      expect(code).toBe(0)
      expect(result).toEqual(expected)
    })
  })
})
