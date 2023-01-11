import React, { useState, useEffect } from "react"
import { Menu, Dropdown, Row, Col, Space } from "antd"
import { Link, useHistory, useLocation, useSelector } from "umi"

import t from '@/utils/t'
import { ROLES, getRolesLabel } from '@/constants/user'
import { getDeployUrl } from '@/constants/common'
import useFetch from '@/hooks/useFetch'

import LangBtn from "../common/langBtn"

import styles from "./index.less"
import './menu.less'
import logo from '@/assets/logo_a.png'
import { NavHomeIcon, NavModelmanageIcon, NavDatasetIcon, ArrowDownIcon } from '@/components/common/Icons'
import { GithubIcon, UserIcon, NavTaskIcon, FlagIcon, EqualizerIcon, StoreIcon } from "../common/Icons"
import {
  LogoutOutlined,
} from "@ant-design/icons"

const menus = () => [
  {
    label: 'common.top.menu.home',
    key: "/home/portal",
    icon: <NavHomeIcon className={styles.navIcon} />,
  },
  {
    label: 'common.top.menu.project',
    key: "/home/project",
    icon: <NavTaskIcon className={styles.navIcon} />,
  },
  {
    label: 'common.top.menu.keyword',
    key: "/home/keyword",
    icon: <FlagIcon className={styles.navIcon} />,
  },
  {
    label: 'algo.public.label',
    key: "/home/algo",
    icon: <StoreIcon className={styles.navIcon} />,
    hidden: !getDeployUrl(),
  },
  {
    label: 'common.top.menu.public_image',
    key: "/home/public_image",
    icon: <EqualizerIcon className={styles.navIcon} />,
  },
]

function getParantPath(path) {
  return path.replace(/^(\/home\/[^\/]+).*/, "$1")
}

function validPermission(role, permission) {
  return role >= (permission || role)
}

function HeaderNav({ simple = false }) {
  const [defaultKeys, setDefaultKeys] = useState(null)
  const location = useLocation()
  const history = useHistory()
  const [mainMenu, setMainMenu] = useState([])
  const { avatar, role, username, email } = useSelector(({ user }) => user)
  const [logoutResult, loginout] = useFetch('user/loginout')

  useEffect(() => {
    const key = getParantPath(location.pathname)
    setDefaultKeys([key])
  }, [location.pathname])

  useEffect(() => {
    setMainMenu(handleMenus(menus()))
  }, [role])

  useEffect(() => logoutResult && history.push('/login'), [logoutResult])

  const out = () => loginout()

  const handleClick = ({ key }) => {
    setDefaultKeys([key])
    history.push(key)
  }
  const topMenuItems = [
    { key: 'user', label: <div onClick={() => history.push('/home/user')}><UserIcon /> {t('common.top.menu.user')}</div>, },
    { key: 'github', label: <a target="_blank" href='https://github.com/IndustryEssentials/ymir'><GithubIcon /> {t('common.top.menu.community')}</a>, },
    { key: 'logout', label: <div onClick={out}><LogoutOutlined /> {t('common.top.menu.logout')}</div>, },
  ]

  const menu = <Menu className={styles.popMenu} items={topMenuItems} />

  const renderSimple = (
    <Col flex={1} style={{ textAlign: 'right' }}>
      <LangBtn />
    </Col>
  )

  const handleMenus = (menus) => {
    let result = []
    menus.forEach(menu => {
      if (menu.children) {
        menu.children = handleMenus(menu.children)
      }
      menu.label = t(menu.label)
      !menu.hidden && validPermission(role, menu.permission) && result.push(menu)
    })
    return result
  }

  const name = `${role > ROLES.USER ? `${t(getRolesLabel(role))} -` : ''}${username || email}`

  return (
    <Row className={styles.nav} gutter={24} align="middle">
      <div className={styles.logo} style={{ overflow: simple ? 'initial' : 'hidden' }}><Link to='/' title={'YMIR'}><img src={logo} /></Link></div>
      {!simple ? <>
        <Col flex={1}>
          <Menu className='nav-menu' selectedKeys={defaultKeys} onClick={handleClick} mode="horizontal" items={mainMenu} />
        </Col>
        {/* // todo add search entrance */}
        <Col style={{ textAlign: "right" }}>
          <Space size={20}>
            <Dropdown overlay={menu} placement="bottomRight">
              <div className={styles.user} title={name}>
                <span className={styles.avatar}>{avatar ? <img src={avatar} /> : (username || 'Y').charAt(0).toUpperCase()}</span>
                <span className={styles.username}>{name}</span>
                <ArrowDownIcon />
              </div>
            </Dropdown>
            <LangBtn />
          </Space>
        </Col>
      </> : renderSimple}
    </Row>
  )
}

export default HeaderNav
