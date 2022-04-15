import { ROLES,
  STATES,
  getRolesLabel,
  getUserState } from '../user'

describe("constants: user", () => {
  it("ROLES: user roles have right mapping and object is freeze", () => {
    expect(ROLES.SUPER).toBe(3)
    expect(ROLES.ADMIN).toBe(2)
    expect(ROLES.USER).toBe(1)

    function tryExtendAttr () { ROLES.newAttr = 'test' }
    expect(tryExtendAttr).toThrowError('object is not extensible')
  })
  it("STATES: user states have right mapping and object is freeze", () => {
    expect(STATES.REGISTERED).toBe(1)
    expect(STATES.ACTIVE).toBe(2)
    expect(STATES.DECLINED).toBe(3)
    expect(STATES.DEACTIVED).toBe(4)

    function tryExtendAttr () { STATES.newAttr = 'test' }
    expect(tryExtendAttr).toThrowError('object is not extensible')
  })
  it('getRolesLabel: get user role label', () => {

    expect(getRolesLabel(ROLES.SUPER)).toBe('user.role.super')
    expect(getRolesLabel(ROLES.ADMIN)).toBe('user.role.admin')
    expect(getRolesLabel(ROLES.USER)).toBe('user.role.user')
  
    const allLabels = getRolesLabel()
    expect(allLabels[ROLES.SUPER]).toBe('user.role.super')
    expect(allLabels[ROLES.ADMIN]).toBe('user.role.admin')
    expect(allLabels[ROLES.USER]).toBe('user.role.user')

    expect(getRolesLabel('54')).toBe(undefined) // unmatch role
  })
  it('getUserState: get label of user states', () => {

    expect(getUserState(STATES.REGISTERED)).toBe('user.state.registered')
    expect(getUserState(STATES.ACTIVE)).toBe('user.state.active')
    expect(getUserState(STATES.DECLINED)).toBe('user.state.declined')
    expect(getUserState(STATES.DEACTIVED)).toBe('user.state.deactived')
  
    const allLabels = getUserState()
    expect(allLabels[STATES.REGISTERED]).toBe('user.state.registered')
    expect(allLabels[STATES.ACTIVE]).toBe('user.state.active')
    expect(allLabels[STATES.DECLINED]).toBe('user.state.declined')
    expect(allLabels[STATES.DEACTIVED]).toBe('user.state.deactived')

    expect(getUserState('54')).toBe(undefined) // unmatch state

  })
})
