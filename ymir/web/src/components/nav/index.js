import React, { useState, useEffect } from "react"
import { Menu, Dropdown, Row, Col, Space } from "antd"
import {
  LogoutOutlined,
} from "@ant-design/icons"
import { connect } from "dva"
import { Link, useHistory, useLocation } from "umi"

import t from '@/utils/t'
import { ROLES } from '@/constants/user'
import LangBtn from "../common/langBtn"
import styles from "./index.less"
import './menu.less'
import logo from '@/assets/logo_a.png'
import { NavHomeIcon, NavModelmanageIcon, NavDatasetIcon, ArrowDownIcon } from '@/components/common/icons'
import { GithubIcon, UserIcon, NavTaskIcon, FlagIcon, EqualizerIcon } from "../common/icons"

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
    label: 'common.top.menu.configure',
    key: "/home/configures",
    icon: <EqualizerIcon className={styles.navIcon} />,
    children: [
      {
        label: 'common.top.menu.image',
        key: "/home/image",
      },
      {
        label: 'common.top.menu.permission',
        key: "/home/permission",
        permission: ROLES.SUPER,
      },
    ]
  },
]

function getParantPath(path) {
  return path.replace(/^(\/home\/[^\/]+).*/, "$1")
}

function validPermission(role, permission) {
  return role >= (permission || role)
}

function HeaderNav({ simple = false, username, loginout, avatar, role }) {
  const [defaultKeys, setDefaultKeys] = useState(null)
  const location = useLocation()
  const history = useHistory()
  const [mainMenu, setMainMenu] = useState([])

  useEffect(() => {
    const key = getParantPath(location.pathname)
    setDefaultKeys([key])
  }, [location.pathname])

  useEffect(() => {
    setMainMenu(handleMenus(menus()))
  }, [role])

  const out = async () => {
    const res = await loginout()
    if (res) {
      history.push("/login")
    }
  }

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
      validPermission(role, menu.permission) && result.push(menu)
    })
    return result
  }

  return (
    <Row className={styles.nav} gutter={24} align="middle">
      <div className={styles.logo} style={{ overflow: simple ? 'initial' : 'hidden' }}><Link to='/' title={'YMIR'}><img src={logo} /></Link></div>
      {!simple ? <>
        <Col flex={1}>
          <Menu className='nav-menu' selectedKeys={defaultKeys} onClick={handleClick} mode="horizontal" items={mainMenu} />
        </Col>
        <Col style={{ textAlign: "right" }}>
          <Space size={20}>
            <Dropdown overlay={menu} placement="bottomRight">
              <div className={styles.user}>
                <span className={styles.avatar}>{avatar ? <img src={avatar} /> : (username || 'Y').charAt(0).toUpperCase()}</span>
                <span>{username}</span>
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

const mapStateToProps = (state) => {
  return {
    logined: state.user.logined,
    username: state.user.username,
    avatar: state.user.avatar,
    current: state.watchRoute.current,
    role: state.user.role,
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    updateCurrentPath(newPath) {
    },
    loginout() {
      return dispatch({
        type: "user/loginout",
      })
    },
  }
}
export default connect(mapStateToProps, mapDispatchToProps)(HeaderNav)
