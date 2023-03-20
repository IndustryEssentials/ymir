import { useState, useEffect, FC, ReactChild } from 'react'
import { Menu, Dropdown, Row, Col, Space } from 'antd'
import { useSelector } from 'react-redux'
import { Link, useHistory, useLocation } from 'umi'
import { MenuItemType } from 'rc-menu/lib/interface'

import t from '@/utils/t'
import { ROLES, getRolesLabel } from '@/constants/user'
import { getDeployUrl } from '@/constants/common'

import LangBtn from '../common/LangBtn'

import styles from './nav.less'
import './menu.less'
import logo from '@/assets/logo_a.png'
import { NavHomeIcon, ArrowDownIcon, GithubIcon, UserIcon, NavTaskIcon, FlagIcon, EqualizerIcon, StoreIcon } from '@/components/common/Icons'
import { LogoutOutlined } from '@ant-design/icons'
import useRequest from '@/hooks/useRequest'

type MenuItem = MenuItemType & {
  label?: string
  key: string
  icon: ReactChild
  hidden?: boolean
  permission?: ROLES
  children?: MenuItem[]
}

const menus = (): MenuItem[] => [
  {
    label: 'common.top.menu.home',
    key: '/home/portal',
    icon: <NavHomeIcon className={styles.navIcon} />,
  },
  {
    label: 'common.top.menu.project',
    key: '/home/project',
    icon: <NavTaskIcon className={styles.navIcon} />,
  },
  {
    label: 'common.top.menu.keyword',
    key: '/home/keyword',
    icon: <FlagIcon className={styles.navIcon} />,
  },
  {
    label: 'algo.public.label',
    key: '/home/algo',
    icon: <StoreIcon className={styles.navIcon} />,
    hidden: !getDeployUrl(),
  },
  {
    label: 'common.top.menu.public_image',
    key: '/home/public_image',
    icon: <EqualizerIcon className={styles.navIcon} />,
  },
]

function getParantPath(path: string) {
  return path.replace(/^(\/home\/[^\/]+).*/, '$1')
}

function validPermission(role: ROLES, permission?: ROLES) {
  return !permission || role >= (permission || role)
}

const HeaderNav: FC<{ simple?: boolean }> = ({ simple = false }) => {
  const [defaultKeys, setDefaultKeys] = useState<string[]>()
  const location = useLocation()
  const history = useHistory()
  const [mainMenu, setMainMenu] = useState<MenuItem[]>([])
  const { avatar, role, username, email } = useSelector<YStates.Root, YStates.UserState>(({ user }) => user)
  const { data: logoutResult, run: loginout } = useRequest<boolean>('user/loginout')

  useEffect(() => {
    const key = getParantPath(location.pathname)
    setDefaultKeys([key])
  }, [location.pathname])

  useEffect(() => {
    setMainMenu(handleMenus(menus()))
  }, [role])

  useEffect(() => {
    logoutResult && history.push('/login')
  }, [logoutResult])

  const out = () => loginout()

  const handleClick = ({ key }: { key: string }) => {
    setDefaultKeys([key])
    history.push(key)
  }
  const topMenuItems = [
    {
      key: 'user',
      label: (
        <div onClick={() => history.push('/home/user')}>
          <UserIcon /> {t('common.top.menu.user')}
        </div>
      ),
    },
    {
      key: 'github',
      label: (
        <a target="_blank" href="https://github.com/IndustryEssentials/ymir">
          <GithubIcon /> {t('common.top.menu.community')}
        </a>
      ),
    },
    {
      key: 'logout',
      label: (
        <div onClick={out}>
          <LogoutOutlined /> {t('common.top.menu.logout')}
        </div>
      ),
    },
  ]

  const menu = <Menu className={styles.popMenu} items={topMenuItems} />

  const renderSimple = (
    <Col flex={1} style={{ textAlign: 'right' }}>
      <LangBtn />
    </Col>
  )

  const handleMenus = (menus: MenuItem[]) => {
    let result: MenuItem[] = []
    menus.forEach((menu) => {
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
      <div className={styles.logo} style={{ overflow: simple ? 'initial' : 'hidden' }}>
        <Link to="/" title={'YMIR'}>
          <img src={logo} />
        </Link>
      </div>
      {!simple ? (
        <>
          <Col flex={1}>
            <Menu className="nav-menu" selectedKeys={defaultKeys} onClick={handleClick} mode="horizontal" items={mainMenu} />
          </Col>
          <Col style={{ textAlign: 'right' }}>
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
        </>
      ) : (
        renderSimple
      )}
    </Row>
  )
}

export default HeaderNav
