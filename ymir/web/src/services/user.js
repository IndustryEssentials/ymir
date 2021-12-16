import request from "@/utils/request"
import { createFd } from "@/utils/transfer"
import CryptoJS from "crypto-js"

function sha1(value) {
  return CryptoJS.SHA1(value).toString()
}

export function signup({ email, username, password, phone = null }) {
  password = sha1(password)
  return request.post("/users/", {
    email,
    username,
    password,
    phone,
  })
}

export async function login(params) {
  params.password = sha1(params.password)
  const fd = createFd(params)
  return request({
    method: "post",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    },
    url: "/auth/token",
    data: fd,
  })
}

export async function loginout(params) {
  const fd = createFd(params)
  return request.post("/auth/loginout", fd)
}

export function getMeInfo() {
  return request.get("/users/me")
}

export function updateUserInfo(info) {
  return request({
    method: 'PATCH',
    url: '/users/me',
    data: info,
  })
}

export function forgetPwd(email) {
  return request.post(`/password-recovery/${email}`)
}

export function modifyPwd(password) {
  password = sha1(password)
  return updateUserInfo({ password })
}
export function resetPwd({ new_password, token }) {
  new_password = sha1(new_password)
  return request.post("/reset-password/", { new_password, token })
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
export function getUsers(params) {
  return request.get('/users/', { params })
}

/**
 * set user state, only for super admin
 * @param {number} id 
 * @param {number} state  user state 
 * @param {number} role user role
 * @returns 
 */
export function setUserState({ id, state, role }) {
  return request({
    url: `/users/${id}`, 
    method: 'PATCH',
    data: { state, role },
  })
}
