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

export function modifyPwd(new_password, old_password) {
  new_password = sha1(new_password)
  old_password = sha1(old_password)
  return request.post("/users/modifyPwd", { new_password, old_password })
}
export function resetPwd({ new_password, token }) {
  new_password = sha1(new_password)
  return request.post("/reset-password/", { new_password, token })
}
