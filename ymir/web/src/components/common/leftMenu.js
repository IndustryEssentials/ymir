import { useEffect, useState } from "react"
import { Menu, Layout } from "antd"
import { useHistory, useLocation, withRouter } from "umi"
import t from '@/utils/t'
import { BarchartIcon, FlagIcon, GithubIcon, FileHistoryIcon, MymodelIcon, NavDatasetIcon, UserIcon, UserSettingsIcon } from '@/components/common/icons'

const { Sider } = Layout

const getItem = (label, key, icon, children, type = '') => ({
  key, icon, children, label, type,
})

const getGroupItem = (label, key, children) => getItem(label, key, undefined, children, 'group')

function LeftMenu() {
  const history = useHistory()
  const { pathname } = useLocation()
  const [defaultKeys, setDefaultKeys] = useState(null)
  const [items, setItems] = useState([])

  useEffect(() => {
    const projectModule = /^.*\/project\/(\d+).*$/
    const showLeftMenu = projectModule.test(pathname)
    const id = pathname.replace(projectModule, '$1')
    console.log('id:', id, pathname, showLeftMenu)
    setItems(showLeftMenu ? [
      getGroupItem(t('breadcrumbs.projects'), 'project', [
        getItem(t('project.summary'), `/home/project/${id}/detail`, <BarchartIcon />,),
        getItem(t('dataset.list'), `/home/project/${id}/dataset`, <NavDatasetIcon />,),
        getItem(t('model.management'), 'model', <MymodelIcon />, [
          getItem(t('model.list'), `/home/project/${id}/model`),
          getItem(t('breadcrumbs.task.training'), `/home/task/train/${id}`),
          getItem(t('model.diagnose'), `/home/project/${id}/diagnose`),
        ]),
      ]),
      getGroupItem(t('breadcrumbs.keyword'), 'keyword', [
        getItem(t('breadcrumbs.keyword'), '/home/keyword', <FlagIcon />,),
      ]),
      getGroupItem(t('common.top.menu.configure'), 'settings', [
        getItem(t('common.top.menu.image'), '/home/image', <FileHistoryIcon />,),
        getItem(t('common.top.menu.permission'), '/home/permission', <UserSettingsIcon />,),
      ]),
      { type: 'divider' },
      getItem(t('user.settings'), '/home/user', <UserIcon />,),
      getItem(<a target="_blank" href='https://github.com/IndustryEssentials/ymir'><GithubIcon /> {t('common.top.menu.community')}</a>, 'github',),
    ] : [])
  }, [pathname])

  const clickHandle = ({ key }) => {
    setDefaultKeys([key])
    history.push(key)
  }

  return items.length ? (
    <Sider style={{ background: '#fff' }}>
      <Menu items={items} mode='inline' defaultOpenKeys={['model']} onClick={clickHandle} selectedKeys={defaultKeys}></Menu>
    </Sider>
  ) : null
}

export default withRouter(LeftMenu)
