// import { history } from "umi"
import { message } from "antd"
import storage from "@/utils/storage"
import t from "@/utils/t"
import {
  login,
  loginout,
  modifyPwd,
  resetPwd,
  forgetPwd,
  getMeInfo,
  updateUserInfo,
  signup,
} from "@/services/user"

const neverShow = storage.get("never_show")

const model = {
  namespace: "user",
  state: {
    username: "",
    email: "",
    phone: "",
    avatar: '',
    id: 0,
    logined: !!storage.get("access_token"),
    neverShow,
    guideVisible: false,
  },
  effects: {
    *setGuideVisible({ payload }, { put }) {
      const visible = !!payload
      yield put({ type: 'UPDATE_GUIDE_VISIBLE', payload: visible})
    },
    *setNeverShow({ payload }, { put }) {
      const neverShow = !!payload
      yield put({ type: 'UPDATE_NEVER_SHOW', payload: neverShow})
    },
    *signup({ payload }, { call, put, select }) {
      const { code, result } = yield call(signup, payload)
      if (code === 0) {
        return result
      }
    },
    *login({ payload }, { call, put, select }) {
      const neverShow = yield select(({ user }) => user.neverShow)
      const { code, result } = yield call(login, payload)
      const { access_token } = result
      if (code === 0 && access_token) {
        storage.set("access_token", access_token || "")
        message.success(t("login.login.success"))
        yield put({ type: 'setGuideVisible', payload: !neverShow })
        yield put({ type: "UPDATE_LOGINED", payload: true })
        yield put({ type: "getUserInfo" })
      }
      return result
    },
    *forgetPwd({ payload }, { call, put, select }) {
      const { code, result } = yield call(forgetPwd, payload)
      if (code === 0) {
        message.success(t("forget.send.success"))
        return true
      }
    },
    // *modifyPwd({ payload }, { call, put, select }) {
    //   const { code, result } = yield call(modifyPwd, payload)
    //   if (code === 0) {
    //     return result
    //   }
    // },
    *resetPwd({ payload }, { call, put, select }) {
      const { code, result } = yield call(resetPwd, payload)
      return code === 0
    },
    *getUserInfo({ payload }, { call, put, select }) {
      const user = yield select(({ user }) => user)
      if (!payload && user.id) {
        return user
      }
      const { result } = yield call(getMeInfo)
      if (result) {
        yield put({
          type: "UPDATE_USERINFO",
          payload: result,
        })
        return result
      }
    },
    *updateUserInfo({ payload }, { call, put, select }) {
      const { result } = yield call(updateUserInfo, payload)
      if (result) {
        yield put({
          type: "UPDATE_USERINFO",
          payload: result,
        })
        return result
      }
    },
    *loginout({ payload }, { call, put, select }) {
      storage.remove("access_token")
      yield put({ type: "UPDATE_LOGINED", payload: false })
      yield put({ type: 'UPDATE_USERINFO', payload: {
        username: '',
        email: '',
        id: '',
        phone: '',
      }})
      return true
    },
  },
  reducers: {
    UPDATE_USERINFO(state, { payload }) {
      return {
        ...state,
        username: payload.username,
        email: payload.email,
        phone: payload.phone,
        avatar: payload.avatar,
        id: payload.id,
      }
    },
    UPDATE_LOGINED(state, { payload }) {
      return {
        ...state,
        logined: payload,
      }
    },
    UPDATE_GUIDE_VISIBLE(state, { payload }) {
      return {
        ...state,
        guideVisible: payload,
      }
    },
    UPDATE_NEVER_SHOW(state, { payload }) {
      storage.set('never_show', payload ? 1 : 0)
      return {
        ...state,
        neverShow: payload,
      }
    },
  },
}
export default model
