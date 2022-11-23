import { Button, Dropdown, Menu, Space } from "antd"
import s from './table.less'
import { More1Icon } from "../common/Icons"
import React from "react"

type Props = {
  actions: YComponents.Action[],
  showCount?: number,
}

const renderActions = (menus: YComponents.Action[]) => menus.map((menu, i) => renderAction(menu, i === menus.length - 1))

const isOuterLink = (link: string) => /^http(s)?:/i.test(link)

const moreActions = (ations: YComponents.Action[]) => <Menu
  className={s.more}
  style={{ color: 'rgba(0, 0, 0, 0.65)' }}
  items={ations.map(action => ({
    key: action.key,
    label: renderAction(action)
  }))} />

function renderAction(action: YComponents.Action, last: boolean = false) {
  const { key, onclick = () => { }, icon, label, link, target, disabled } = action
  const cls = `${s.action} ${last ? s.last : ''}`
  const btn = (
    <Button key={key} type='link' disabled={disabled} className={cls} onClick={() => onclick()}>
      {icon}{label}
    </Button>
  )
  return link ? <a
    key={key}
    className={`${cls} ant-btn ant-btn-link`}
    target={target ? target : (isOuterLink(link) ? '_blank' : '')}
    href={link}
  >
    {icon} {label}
  </a> : btn
}

const Actions: React.FC<Props> = ({ actions = [], showCount = 3 }) => {
  const showActions = actions.filter(action => !(action.hidden && action.hidden()))
  const isMore = () => showActions.length > showCount
  return (
    <Space className={s.actions} size={4}>
      {renderActions(showActions.filter((item, i) => i < showCount))}
      {isMore() ? (
        <Dropdown overlay={moreActions(showActions.filter((item, i) => i >= showCount))}>
          <More1Icon />
        </Dropdown>
      ) : null}
    </Space>
  )
}

export default Actions
