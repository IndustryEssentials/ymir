import { history } from "umi"
// import request from '../request'
import storage from "@/utils/storage"
import { message } from "antd"
// console.log('history: ', history)

const token = 'itistokenstring'

jest.mock("umi", () => {
  return {
    history: {
      push: jest.fn(),
      replace: jest.fn(),
      location: {
        pathname: 'testpathname',
      }
    },
  }
})

jest.mock('@/utils/storage', () => {
  return {
    get: jest.fn(() => token),
    remove: jest.fn(),
  }
})

jest.mock('@/utils/t', () => {
  return jest.fn()
})

const err = "it is a test error message"

describe("utils: request", () => {
  let consoleSpy = {}
  let msgSpy = {}

  beforeEach(() => {
    // process.env.APIURL = 'http://192.168.13.107:8088/api/v1/'
    process.env.APIURL = "https://www.baidu.com/"
    consoleSpy = jest.spyOn(console, "error").mockImplementation(() => { })
    msgSpy = jest.spyOn(message, "error").mockImplementation(() => { })
  })

  it("set the right base url", () => {
    const request = require("../request").default

    expect(request.defaults.baseURL).toBe(process.env.APIURL)
  })
  it("a request interceptor to the request", () => {
    const request = require("../request").default
    // const sget = jest.spyOn(storage, "get")
    // const token = test_data
    // sget.mockReturnValue(token)
    const config = { headers: { "Content-Type": "text/plain" } }

    const reqHandler = request.interceptors.request.handlers[0]

    const iconfig = reqHandler.fulfilled(config)

    // request resolve
    expect(iconfig.headers).toHaveProperty(
      "Authorization",
      expect.stringContaining(token)
    )

    // request reject
    const errRes = reqHandler.rejected(err)
    expect(errRes).toBe(err)
  })

  it("a response interceptor to the request", () => {
    const request = require("../request").default

    let res = {
      status: 200,
      data: {
        code: 0,
        result: { access_token: token },
      },
    }

    const err = "it is a test error message"
    const reqHandler = request.interceptors.response.handlers[0]

    const { code, result } = reqHandler.fulfilled(res)

    expect(code).toBe(0)
    expect(result.access_token).toBe(token)

    res = {
      request: {
        statusText: '',
        status: 401,
      },
      response: {
        data: {
          code: 1004,
          message: err,
        }
      }
    }

    expect(() => {
      reqHandler.rejected(res)
    }).toThrow()
    expect(storage.remove).toHaveBeenCalled()
    expect(history.replace).toHaveBeenCalled()
    
    res = {
      request: {
        statusText: '',
        status: 405,
      },
      response: {
        data: {
          code: 2005,
          message: err,
        },
      },
    }

    // expect(() => {
    reqHandler.rejected(res)
    // }).toThrow()
    expect(msgSpy).toHaveBeenCalled()
  })
})
