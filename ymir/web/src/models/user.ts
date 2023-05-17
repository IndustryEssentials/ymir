import { message } from 'antd'
import storage from '@/utils/storage'
import t from '@/utils/t'
import { login, modifyPwd, resetPwd, forgetPwd, getMeInfo, updateUserInfo, getUsers, setUserState, setUserRole, signup, refreshToken } from '@/services/user'
import { ROLES, STATES } from '@/constants/user'
import { UserState, UserStore } from '.'
import { createEffect, createReducersByState } from './_utils'
import { User } from '@/constants'

const setToken = (token?: string) => {
  storage.set('access_token', token || '')
}
const emptyUser = {
  id: 0,
  hash: '',
  email: '',
  role: ROLES.USER,
  uuid: '',
}

const state: UserState = {
  user: emptyUser,
  logined: !!storage.get('access_token'),
}

const model: UserStore = {
  namespace: 'user',
  state,
  effects: {
    signup: createEffect(function* ({ payload }, { call, put, select }) {
      const { code, result } = yield call(signup, payload)
      if (code === 0) {
        return result
      }
    }),
    login: createEffect(function* ({ payload }, { call, put, select }) {
      const { code, result } = yield call(login, payload)
      if (code === 0 && result?.access_token) {
        storage.set('access_token', result.access_token || '')
        message.success(t('login.login.success'))
        yield put({ type: 'UpdateLogined', payload: true })
        yield put({ type: 'getUserInfo' })
      }
      return result
    }),
    getToken: createEffect(function* ({ payload }, { call, put, select }) {
      const { code, result } = yield call(login, payload)
      if (code === 0) {
        setToken(result?.access_token)
      }
      return result
    }),
    setToken({ payload: token }) {
      storage.set('access_token', token || '')
    },
    refreshToken: createEffect(function* ({ payload }, { call, put, select }) {
      const { code, result } = yield call(refreshToken)
      if (code === 0) {
        setToken(result?.access_token)
      }
    }),
    forgetPwd: createEffect(function* ({ payload }, { call, put, select }) {
      const { code, result } = yield call(forgetPwd, payload)
      if (code === 0) {
        message.success(t('forget.send.success'))
        return true
      }
    }),
    modifyPwd: createEffect(function* ({ payload }, { call, put }) {
      const { code, result } = yield call(modifyPwd, payload)
      if (code === 0) {
        yield put({
          type: 'UpdateUser',
          payload: result,
        })
        return result
      }
    }),
    resetPwd: createEffect(function* ({ payload }, { call, put, select }) {
      const { code, result } = yield call(resetPwd, payload)
      return code === 0
    }),
    getUserInfo: createEffect(function* ({ payload }, { call, put, select }) {
      const user: User = yield select(({ user }) => user)
      if (!payload && user.id) {
        return user
      }
      const { result } = yield call(getMeInfo)
      if (result) {
        yield put({
          type: 'UpdateUser',
          payload: result,
        })
        return result
      }
    }),
    updateUserInfo: createEffect(function* ({ payload }, { call, put, select }) {
      const { result } = yield call(updateUserInfo, payload)
      if (result) {
        yield put({
          type: 'UpdateUser',
          payload: result,
        })
        return result
      }
    }),
    loginout: createEffect(function* ({}, { call, put, select }) {
      storage.remove('access_token')
      yield put({ type: 'UpdateLogined', payload: false })
      yield put({ type: 'UpdateUser', payload: emptyUser })
      return true
    }),
    getActiveUsers: createEffect(function* ({ payload }, { call }) {
      const { result } = yield call(getUsers, { ...payload, state: STATES.ACTIVE })
      if (result) {
        return result
      }
    }),
    getUsers: createEffect(function* ({ payload }, { call }) {
      const { result } = yield call(getUsers, payload)
      if (result) {
        return result
      }
    }),
    setUserRole: createEffect(function* ({ payload }, { call }) {
      const { id, role } = payload
      const { result } = yield call(setUserRole, { id, role })
      if (result) {
        return result
      }
    }),
    setUserState: createEffect(function* ({ payload }, { call }) {
      const { result } = yield call(setUserState, payload)
      if (result) {
        return result
      }
    }),
    off: createEffect(function* ({ payload }, { call }) {
      const { result } = yield call(setUserState, { id: payload, state: STATES.DEACTIVED })
      if (result) {
        return result
      }
    }),
  },
  reducers: createReducersByState(state),
}
export default model
