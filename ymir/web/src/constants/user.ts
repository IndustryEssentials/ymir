export enum ROLES {
  SUPER = 3,
  ADMIN = 2,
  USER = 1,
}

export enum STATES {
  REGISTERED = 1,
  ACTIVE = 2,
  DECLINED = 3,
  DEACTIVED = 4,
}

export const getRolesLabel = (role: ROLES) => {
  const labels = {
    [ROLES.SUPER]: 'super',
    [ROLES.ADMIN]: 'admin',
    [ROLES.USER]: 'user',
  }
  return `user.role.${labels[role]}`
}

export const getUserState = (state: STATES) => {
  const states = Object.freeze({
    [STATES.REGISTERED]: 'registered',
    [STATES.ACTIVE]: 'active',
    [STATES.DECLINED]: 'declined',
    [STATES.DEACTIVED]: 'deactived',
  })

  return `user.state.${states[state]}`
}

export function isSuperAdmin(role: ROLES) {
  return ROLES.SUPER === role
}
