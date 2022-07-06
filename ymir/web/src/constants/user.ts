
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
    [ROLES.SUPER]: 'super',
    [ROLES.ADMIN]: 'admin',
    [ROLES.USER]: 'user',
  })
  return typeof role !== 'undefined' ? `user.role.${labels[role]}` : labels
}

export const getUserState = (state: number | undefined) => {
  const states = Object.freeze({
    [STATES.REGISTERED]: 'registered',
    [STATES.ACTIVE]: 'active',
    [STATES.DECLINED]: 'declined',
    [STATES.DEACTIVED]: 'deactived',
  })

  return typeof state !== 'undefined' ? `user.state.${states[state]}` : states
}

export function isSuperAdmin(role: number) {
  return ROLES.SUPER === role
}
