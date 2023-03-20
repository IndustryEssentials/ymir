import { ROLES,
  STATES,
  getRolesLabel,
  getUserState } from '../user'

describe("constants: user", () => {
  it("ROLES: user roles have right mapping and object is freeze", () => {
    expect(ROLES.SUPER).toBe(3)
    expect(ROLES.ADMIN).toBe(2)
    expect(ROLES.USER).toBe(1)
  })
  it("STATES: user states have right mapping and object is freeze", () => {
    expect(STATES.REGISTERED).toBe(1)
    expect(STATES.ACTIVE).toBe(2)
    expect(STATES.DECLINED).toBe(3)
    expect(STATES.DEACTIVED).toBe(4)
  })
  it('getRolesLabel: get user role label', () => {

    expect(getRolesLabel(ROLES.SUPER)).toBe('user.role.super')
    expect(getRolesLabel(ROLES.ADMIN)).toBe('user.role.admin')
    expect(getRolesLabel(ROLES.USER)).toBe('user.role.user')
  })
  it('getUserState: get label of user states', () => {

    expect(getUserState(STATES.REGISTERED)).toBe('user.state.registered')
    expect(getUserState(STATES.ACTIVE)).toBe('user.state.active')
    expect(getUserState(STATES.DECLINED)).toBe('user.state.declined')
    expect(getUserState(STATES.DEACTIVED)).toBe('user.state.deactived')

  })
})
