import { login, loginout, getMeInfo, signup, resetPwd, modifyPwd, forgetPwd, getUsers, setUserState } from "../user"

import { products, requestExample } from './func'

describe("service: user", () => {
  it("login -> success", () => {
    const params = { username: "idol", password: "1q2w3e" }
    const expected = "token"
    requestExample(login, params, expected)
  })
  it("loginout -> success", () => {
    const params = {}
    const expected = "ok"
    requestExample(loginout, params, expected, 'post')
  })
  it("getMeInfo -> success", () => {
    const expected = {
      username: "president",
      email: "test@test.com",
      phone: "13245678908",
      id: 1345,
    }
    requestExample(getMeInfo, null, expected, 'get')
  })

  it('signup -> success', () => {
    const params = { username: "idol", password: "password", email: 'test@test.com' }
    const expected = { access_token: 'itisaaccesstoken' }
    requestExample(signup, params, expected, 'post')
  })
  it('forgetPwd -> success', () => {
    
    const params = { email: 'test@test.com' }
    const expected = "ok"
    requestExample(forgetPwd, params, expected, 'post')
  })
  it('modifyPwd -> success', () => {
    
    const password = 'newpassword'
    const expected = "ok"
    requestExample(modifyPwd, password, expected)
  })
  it('resetPwd -> success', () => {
    
    const params = { old: 'oldpassword', newPassword: 'newpassword' }
    const expected = "ok"
    requestExample(resetPwd, params, expected, 'post')
  })
})
  it('getUsers -> success', () => {
    
    const params = { state: 2 }
    const expected = products(19)
    requestExample(getUsers, params, expected, 'get')
  })
  it('setUserState -> success', () => {
    
    const params = { username: 'new rosa' }
    const expected = "ok"
    requestExample(setUserState, params, expected)
  })
