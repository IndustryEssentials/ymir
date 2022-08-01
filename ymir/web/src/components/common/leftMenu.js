import { useEffect, useState } from "react"
import { Menu, Layout } from "antd"
import { useHistory, useLocation, withRouter, useSelector } from "umi"
import t from '@/utils/t'
import { isSuperAdmin } from '@/constants/user'
import { BarchartIcon, FlagIcon, GithubIcon, FileHistoryIcon, MymodelIcon, 
  NavDatasetIcon, UserIcon, UserSettingsIcon, DiagnosisIcon, EditIcon, EyeOffIcon, TrainIcon } from '@/components/common/icons'
import { ProjectIcon, VectorIcon } from "./icons"

const { Sider } = Layout

const projectModule = /^.*\/project\/(\d+).*$/

const getItem = (label, key, Icon, children, type = '') => ({
  key, icon: Icon ? <Icon /> : null, children, label, type,
})

const getGroupItem = (label, key, children) => getItem(label, key, undefined, children, 'group')

function LeftMenu() {
  const role = useSelector(state => state.user.role)
  const projects = useSelector(state => state.project.projects)
  const history = useHistory()
  const { pathname } = useLocation()
  const [defaultKeys, setDefaultKeys] = useState(null)
  const [items, setItems] = useState([])
  const [id, setId] = useState(null)
  const [project, setProject] = useState({})

  useEffect(() => {
    setDefaultKeys(pathname)
    const id = pathname.replace(projectModule, '$1')
    setId(id)
  }, [pathname])

  useEffect(() => {
    id && projects && setProject(projects[id] || {})
  }, [id, projects])

  useEffect(() => {
    const showLeftMenu = projectModule.test(pathname)
    setItems([
      getGroupItem(t('breadcrumbs.projects'), 'project', [
        getItem(t('projects.title'), `/home/project`, ProjectIcon, ),
        showLeftMenu ? getItem(project.name, `project.summary`, VectorIcon, [
            getItem(t('project.summary'), `/home/project/${id}/detail`, BarchartIcon,),
            getItem(t('dataset.list'), `/home/project/${id}/dataset`, NavDatasetIcon,),
            getItem(t('model.management'), `/home/project/${id}/model`, MymodelIcon,),
            getItem(t('model.diagnose'), `/home/project/${id}/diagnose`, DiagnosisIcon),
            getItem(t('breadcrumbs.task.training'), `/home/project/${id}/train`, TrainIcon),
            getItem(t('common.hidden.list'), `/home/project/${id}/hidden`, EyeOffIcon,),
            getItem(t('project.settings.title'), `/home/project/${id}/add`, EditIcon,),
        ]) : null,
      ]),
      getGroupItem(t('breadcrumbs.keyword'), 'keyword', [
        getItem(t('breadcrumbs.keyword'), '/home/keyword', FlagIcon,),
      ]),
      getGroupItem(t('common.top.menu.configure'), 'settings', [
        getItem(t('common.top.menu.image'), '/home/image', FileHistoryIcon,),
        isSuperAdmin(role) ? getItem(t('common.top.menu.permission'), '/home/permission', UserSettingsIcon,) : null,
      ]),
      { type: 'divider' },
      getItem(t('user.settings'), '/home/user', UserIcon,),
      getItem(<a target="_blank" href='https://github.com/IndustryEssentials/ymir'><GithubIcon /> {t('common.top.menu.community')}</a>, 'github',),
    ])
  }, [id, project, role])

  const clickHandle = ({ key }) => {
    setDefaultKeys([key])
    history.push(key)
  }

  return items.length ? (
    <Sider style={{ background: '#fff' }}>
      <Menu items={items} mode='inline' defaultOpenKeys={['project.summary']} onClick={clickHandle} selectedKeys={defaultKeys}></Menu>
    </Sider>
  ) : null
}
export default withRouter(LeftMenu)
