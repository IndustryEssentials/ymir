import { Button, Dropdown, Menu, Space } from "antd"
import s from './table.less'
import { More1Icon } from "../common/icons"

const actions = (menus) => menus.map((menu, i) => action(menu, i === menus.length - 1))

const isOuterLink = (link) => /^http(s)?:/i.test(link)

const moreActions = (menus) => <Menu
  className={s.more}
  style={{ color: 'rgba(0, 0, 0, 0.65)' }}
  items={menus.map(menu => ({
    key: menu.key,
    label: action(menu)
  }))} />

function action({ key, onclick = () => { }, icon, label, link, target, disabled }, last) {
  const cls = `${s.action} ${last ? s.last : ''}`
  const btn = (
    <Button key={key} type='link' disabled={disabled} className={cls} onClick={onclick}>
      {icon}{label}
    </Button>
  )
  return link ? <a
    key={key}
    className={`${cls} ant-btn ant-btn-link`}
    target={target ? target : (isOuterLink(link) && '_blank')}
    href={link}
  >
    {icon} {label}
  </a> : btn
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
