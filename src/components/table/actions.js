import { Button, Dropdown, Menu, Space } from "antd"
import s from './table.less'
import { More1Icon } from "../common/icons"

const actions = (menus) => menus.map((menu, i) => action(menu, i === menus.length - 1))

const moreActions = (menus) => {
  return (
    <Menu>
      {menus.map((menu) => (
        <Menu.Item key={menu.key}>
          {action(menu)}
        </Menu.Item>
      ))}
    </Menu>
  )
}

function action (menu, last) {
return (
  <Button key={menu.key} type='link' className={`${s.action} ${last ? s.last : ''}`} onClick={menu.onclick}>
    {menu.icon}{menu.label}
  </Button>
)
}

const Actions = ({ menus, showCount = 3 }) => {
  const isMore = () =>  menus.length > showCount
  const showActions = menus.filter(menu => !(menu.hidden && menu.hidden()))
  return (
    <Space className={s.actions} size={4} style={ isMore() ? { justifyContent: 'flex-end', width: '100%'} : {}}>
      {actions(showActions.filter((item, i) => i < showCount))}
      {isMore() ? (
        <Dropdown overlay={moreActions(showActions.filter((item, i) => i >= showCount))}>
          <More1Icon />
        </Dropdown>
      ) : null}
    </Space>
  )
}

export default Actions
