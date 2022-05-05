import React, { useState, useEffect } from "react"
import ReactDOM from "react-dom"
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

const { SubMenu } = Menu

const menus = () => [
  {
    label: t('common.top.menu.home'),
    key: "/home/portal",
    icon: <NavHomeIcon className={styles.navIcon} />,
  },
  {
    label: t('common.top.menu.project'),
    key: "/home/project",
    icon: <NavTaskIcon className={styles.navIcon} />,
  },
  {
    label: t('common.top.menu.keyword'),
    key: "/home/keyword",
    icon: <FlagIcon className={styles.navIcon} />,
  },
  {
    label: t('common.top.menu.configure'),
    key: "/home/configures",
    icon: <EqualizerIcon className={styles.navIcon} />,
    sub: [
      {
        label: t('common.top.menu.image'),
        key: "/home/image",
      },
      {
        label: t('common.top.menu.permission'),
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
  // const location = useLocation()
  const [defaultKeys, setDefaultKeys] = useState(null)
  const location = useLocation()
  const history = useHistory()
  const [searchValue, setSearchValue] = useState('')
  const [visible, setVisible] = useState(false)
  const [guideTarget, setGuideTarget] = useState(null)
  const guideRefs = []

  useEffect(() => {
    if (guideRefs.length && guideRefs[1]) {
      setGuideTarget(guideRefs[1])
    }
  }, [guideRefs])

  useEffect(() => {
    const key = getParantPath(location.pathname)
    setDefaultKeys([key])
  }, [location.pathname])

  const out = async () => {
    const res = await loginout()
    if (res) {
      history.push("/login")
    }
  }

  const handleClick = function (key) {
    setDefaultKeys([key])
    history.push(key)
  }

  const menu = (
    <Menu className={styles.popMenu}>
      <Menu.Item key='user' onClick={() => history.push('/home/user')}>
        <UserIcon /> {t('common.top.menu.user')}
      </Menu.Item>
      <Menu.Item key='github'>
        <a target="_blank" href='https://github.com/IndustryEssentials/ymir'><GithubIcon /> {t('common.top.menu.community')}</a>
      </Menu.Item>
      <Menu.Item key='logout' onClick={out}>
        <LogoutOutlined /> {t('common.top.menu.logout')}
      </Menu.Item>
    </Menu>
  )
  const renderSimple = (
    <Col flex={1} style={{ textAlign: 'right' }}>
      <LangBtn />
    </Col>
  )

  const renderMenu = (menus) => {
    return menus.map((menu, i) => {
      if (menu.sub) {
        return (
          <SubMenu
            key={menu.key}
            popupClassName='nav-submenu'
            title={menu.label}
            icon={menu.icon}
            popupOffset={[0, -2]}
          // onTitleClick={handleTitleClick}
          >
            {renderMenu(menu.sub)}
          </SubMenu>
        )
      } else {
        return validPermission(role, menu.permission) ? (
          <Menu.Item key={menu.key} onClick={() => handleClick(menu.key)} ref={e => {
            const ref = ReactDOM.findDOMNode(e)
            if (ref) {
              guideRefs[i] = ref
            }
          }}>
            {menu.icon}
            {menu.label}
          </Menu.Item>
        ) : null
      }
    })
  }

  return (
    <Row className={styles.nav} gutter={24} align="middle">
      <div className={styles.logo} style={{ overflow: simple ? 'initial' : 'hidden' }}><Link to='/' title={'YMIR'}><img src={logo} /></Link></div>
      {!simple ? <>
        <Col flex={1}>
          <Menu className='nav-menu' selectedKeys={defaultKeys} mode="horizontal">
            {renderMenu(menus())}
          </Menu>
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
