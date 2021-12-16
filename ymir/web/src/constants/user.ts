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
    [ROLES.SUPER]: t('user.role.super'),
    [ROLES.ADMIN]: t('user.role.admin'),
    [ROLES.USER]: t('user.role.user'),
  })
  return typeof role !== 'undefined' ? labels[role] : labels
}

export const getUserState = (state: number | undefined) => {
  const states = Object.freeze({
    [STATES.REGISTERED]: t('user.state.registered'),
    [STATES.ACTIVE]: t('user.state.active'),
    [STATES.DECLINED]: t('user.state.declined'),
    [STATES.DEACTIVED]: t('user.state.deactived'),
  })

  return typeof state !== 'undefined' ? states[state] : states
}
