import t from "@/utils/t"

export const ROLES = Object.freeze({
  SUPER: 3,
  ADMIN: 2,
  USER: 1,
})

export const STATES = Object.freeze({
  REGISTERED: 1,
  ACTIVE: 2,
  DECLINED: 3,
  DEACTIVED: 4,
})

export const getRolesLabel = (role: number | undefined) => {
  const labels = Object.freeze({
    [ROLES.SUPER]: 'user.role.super',
    [ROLES.ADMIN]: 'user.role.admin',
    [ROLES.USER]: 'user.role.user',
  })
  return typeof role !== 'undefined' ? labels[role] : labels
}

export const getUserState = (state: number | undefined) => {
  const states = Object.freeze({
    [STATES.REGISTERED]: 'user.state.registered',
    [STATES.ACTIVE]: 'user.state.active',
    [STATES.DECLINED]: 'user.state.declined',
    [STATES.DEACTIVED]: 'user.state.deactived',
  })

  return typeof state !== 'undefined' ? states[state] : states
}
