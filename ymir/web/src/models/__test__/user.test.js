import user from "../user"
import storage from "@/utils/storage"
import { put, select, call } from "redux-saga/effects"

jest.mock('@/utils/t', () => {
  return jest.fn()
})

describe("models: user", () => {
  const Expected = {
    username: "president",
    email: "test@test.com",
    phone: "13245678908",
    id: 1345,
  }
  it("reducers: UPDATE_USERINFO, UPDATE_LOGINED", () => {
    const state = {
      username: "",
      password: "",
      email: "",
      phone: "",
      id: 0,
      logined: false,
    }
    const expected = Expected
    const action = {
      payload: expected,
    }
    const { username, email, phone, id } = user.reducers.UPDATE_USERINFO(
      state,
      action
    )
    expect(username).toBe(expected.username)
    expect(email).toBe(expected.email)
    expect(phone).toBe(expected.phone)
    expect(id).toBe(expected.id)

    const expectedLogined = true
    const actionLogined = {
      payload: expectedLogined,
    }

    const { logined } = user.reducers.UPDATE_LOGINED(state, actionLogined)
    expect(logined).toBe(expectedLogined)
  })

  it('effects: signup', () => {
    const saga = user.effects.signup
    const creator = {
      type: 'signup',
      payload: {
        username: 'username',
        password: 'mockpassword',
      },
    }
    const expected = { usernmae: 'username', access_token: 'thisisaaccesstoken' }
    const generator = saga(creator, { call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: expected,
    })

    expect(end.done).toBe(true)
  })
  it('effects: forgetPwd', () => {
    const saga = user.effects.forgetPwd
    const creator = {
      type: 'forgetPwd',
      payload: {},
    }
    const expected = true
    const generator = saga(creator, { call })
    generator.next()
    const end = generator.next({
      code: 0,
    })

    expect(end.value).toBe(expected)
    expect(end.done).toBe(true)
  })
  it('effects: resetPwd', () => {
    const saga = user.effects.resetPwd
    const creator = {
      type: 'resetPwd',
      payload: {},
    }
    const generator = saga(creator, { call })
    generator.next()
    const end = generator.next({
      code: 0,
    })

    expect(end.value).toBe(true)
    expect(end.done).toBe(true)
  })

  it("effects: login", () => {
    const saga = user.effects.login
    const creator = {
      type: "login",
      payload: {},
    }
    const expected = { access_token: '1234adfkjasldkfj' }

    const generator = saga(creator, { put, call, select })
    generator.next()
    generator.next()
    const ca = generator.next({
      code: 0,
      result: expected,
    })
    generator.next()
    const updateLogined = generator.next()
    const end = generator.next()

    expect(end.done).toBe(true)

    // console.log("login: ", ca, updateLogined, end)
  })
  it("effects: getUserInfo -> get user from network", () => {
    const saga = user.effects.getUserInfo
    const creator = {
      type: "getUserInfo",
    }
    const expected = Expected

    let userinfo = { id: 0 }

    // get use info from remote
    const generator = saga(creator, { put, call, select })
    generator.next()
    const getCacheUser = generator.next(userinfo)
    const getUserInfo = generator.next({
      code: 0,
      result: expected,
    })
    const end = generator.next()

    expect(JSON.stringify(end.value)).toBe(JSON.stringify(expected))
    expect(end.done).toBe(true)
    // console.log('get user info from remote: ', getCacheUser, getUserInfo, end)
  })
  it("effects: getUserInfo -> get cache user", () => {
    const saga = user.effects.getUserInfo
    const creator = {
      type: "getUserInfo",
    }

    const userinfo = { id: 3434 }

    // get use info from cache
    const generator = saga(creator, { put, call, select })
    generator.next()
    const end = generator.next(userinfo)

    expect(end.value.id).toBe(userinfo.id)
    expect(end.done).toBe(true)
  })
  it("effects: getUserInfo -> always get info from net", () => {
    const saga = user.effects.getUserInfo
    const expected = Expected

    const creator = {
      type: "getUserInfo",
      payload: true, // always get info from net
    }

    const userinfo = { id: 3434 }

    const generator = saga(creator, { put, call, select })
    generator.next()
    const getCacheUser = generator.next(userinfo)
    const getUserInfo = generator.next({
      code: 0,
      result: expected,
    })
    const end = generator.next()

    expect(JSON.stringify(end.value)).toBe(JSON.stringify(expected))
    expect(end.done).toBe(true)
  })
  it("effects: loginout", () => {
    const saga = user.effects.loginout
    const creator = {
      type: "loginout",
      payload: {},
    }
    const expected = true

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next()
    const end = generator.next()

    expect(end.value).toBe(true)
    expect(end.done).toBe(true)
  })

  it("effects: setGuideVisible", () => {
    const saga = user.effects.setGuideVisible
    const creator = {
      type: "setGuideVisible",
      payload: true,
    }

    const generator = saga(creator, { put })
    generator.next()
    const end = generator.next()

    expect(end.done).toBe(true)
  })
  
  it("effects: setNeverShow", () => {
    const saga = user.effects.setNeverShow
    const creator = {
      type: "setNeverShow",
      payload: false,
    }

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next()

    expect(end.done).toBe(true)
  })
  
  it("effects: getToken", () => {
    const saga = user.effects.getToken
    const creator = {
      type: "getToken",
      payload: {username: 'username007@test.com', password: '12345689' },
    }
    const expected = 'access_token'

    const generator = saga(creator, { put, call })
    generator.next()
    const end = generator.next({
      code: 0,
      result: {
        access_token: expected,
      }
    })

    expect(end.value.access_token).toBe(expected)
    expect(storage.get('access_token')).toBe(expected)
    expect(end.done).toBe(true)
  })
  
  it("effects: modifyPwd", () => {
    const saga = user.effects.modifyPwd
    const newUser = { id: 346, password: 'newpassw0rd' }
    const creator = {
      type: "modifyPwd",
      payload: newUser.password,
    }
    const expected = { id: newUser.id }

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: expected,
    })
    const end = generator.next()

    expect(end.value.id).toBe(newUser.id)
    expect(end.done).toBe(true)
  })
  
  it("effects: updateUserInfo", () => {
    const saga = user.effects.updateUserInfo
    
    const newUser = { id: 347, name: 'newusername' }
    const creator = {
      type: "updateUserInfo",
      payload: { name: newUser.name },
    }
    const expected = { id: newUser.id, name: newUser.name }

    const generator = saga(creator, { put, call })
    generator.next()
    generator.next({
      code: 0,
      result: expected
    })
    const end = generator.next()

    expect(end.value.id).toBe(newUser.id)
    expect(end.value.name).toBe(newUser.name)
    expect(end.done).toBe(true)
  })
})
