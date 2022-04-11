import { Button, Dropdown, Menu, Space } from "antd"
import s from './table.less'
import { More1Icon } from "../common/icons"

const actions = (menus) => menus.map((menu, i) => action(menu, i === menus.length - 1))

const isOuterLink = (link) => /^http(s)?:/i.test(link)

const moreActions = (menus) => {
  return (
    <Menu>
      {menus.map((menu) => (
        <Menu.Item key={menu.key}>
          {menu.link ? <a target={menu.target ? menu.target : (isOuterLink(menu.link) && '_blank')} href={menu.link}>{action(menu)}</a> : action(menu)}
        </Menu.Item>
      ))}
    </Menu>
  )
}

function action({ key, onclick = () => { }, icon, label, link, target, disabled }, last) {
  const btn = (
    <Button key={key} type='link' disabled={disabled} className={`${s.action} ${last ? s.last : ''}`} onClick={onclick}>
      {icon}{label}
    </Button>
  )
  return link ? <a key={key} target={target ? target : (isOuterLink(link) && '_blank')} href={link}>{btn}</a> : btn
}

const Actions = ({ menus, showCount = 3 }) => {
  const showActions = menus.filter(menu => !(menu.hidden && menu.hidden()))
  const isMore = () => showActions.length > showCount
  return (
    <Space className={s.actions} size={4}>
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
