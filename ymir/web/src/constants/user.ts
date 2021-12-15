import t from "@/utils/t"

export const ROLES = Object.freeze({
  SUPER: 2,
  ADMIN: 1,
  USER: 0,
})

export const STATES = Object.freeze({
  REGISTED: 1,
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
    [STATES.REGISTED]: t('user.state.registed'),
    [STATES.ACTIVE]: t('user.state.active'),
    [STATES.DECLINED]: t('user.state.declined'),
    [STATES.DEACTIVED]: t('user.state.deactived'),
  })

  return typeof state !== 'undefined' ? states[state] : states
}
