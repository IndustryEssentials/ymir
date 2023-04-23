import request from '@/utils/request'
import { createFd } from '@/utils/object'
import CryptoJS from 'crypto-js'
import { LoginParams, QueryUsersParams, ResetPwdParams, SignupParams, UpdatePermissionParams, UpdateUserParams } from './typings/user'

function sha1(value: string) {
  return CryptoJS.SHA1(value).toString()
}

export function signup({ email, username, password, phone, organization, scene }: SignupParams) {
  password = sha1(password)
  return request.post('/users/', {
    email,
    username,
    password,
    phone,
    organization,
    scene,
  })
}

export async function login(params: LoginParams) {
  params.password = sha1(params.password)
  const fd = createFd(params)
  return request({
    method: 'post',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    },
    url: '/auth/token',
    data: fd,
  })
}

export function getMeInfo() {
  return request.get('/users/me')
}

export function updateUserInfo(info: UpdateUserParams) {
  return request({
    method: 'PATCH',
    url: '/users/me',
    data: info,
  })
}

export function forgetPwd(email: string) {
  return request.post(`/password-recovery/${email}`)
}

export function modifyPwd(password: string) {
  password = sha1(password)
  return updateUserInfo({ password })
}
export function resetPwd({ new_password, token }: ResetPwdParams) {
  new_password = sha1(new_password)
  return request.post('/reset-password/', { new_password, token })
}

/**
 * get users, only for super admin
 * @param {object} params
 * {
 *   limit   20
 *   offset  0
 *   state   user state, registered = 1 active = 2 declined = 3 deactivated = 4
 * }
 * @returns
 */
export function getUsers(params: QueryUsersParams) {
  return request.get('/users/', { params })
}

/**
 * @description set user state, only for super admin
 * @export
 * @param {UpdatePermissionParams} { id, state, role }
 */
export function setUserState({ id, state, role }: UpdatePermissionParams) {
  return request({
    url: `/users/${id}`,
    method: 'PATCH',
    data: { state, role },
  })
}

export function refreshToken() {
  return request.post('/auth/refresh_token_name')
}
