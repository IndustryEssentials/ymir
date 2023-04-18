import { ROLES, STATES } from '@/constants/user'

type AuthParams = {
  email: string
  password: string
}
type SignupParams = AuthParams & {
  username?: string
  phone?: string
  organization?: string
  scene?: string
}

type LoginParams = AuthParams

type UpdateUserParams = { 
  password?: string
  phone?: string
  username?: string
  avatar?: string
}

type ResetPwdParams = {
  new_password: string
  token: string
}

type UpdatePermissionParams = {
  id: number
  role: ROLES
  state: STATES
}

type QueryUsersParams = {
  limit: number
  offset: number
  state: STATES
}

export { SignupParams, LoginParams, UpdateUserParams, ResetPwdParams, UpdatePermissionParams, QueryUsersParams }
