import { Breadcrumb } from "antd"
import { Link, useHistory, useParams, useRouteMatch, } from "umi"
import t from '@/utils/t'
import s from './common.less'

const { Item } = Breadcrumb

const getCrumbs = () => [
  { path: '/home/portal', label: t('breadcrumbs.portal'), pid: 0, id: 1 },
  { path: '/home/task/:keyword?', label: t('breadcrumbs.tasks'), pid: 1, id: 2 },
  { path: '/home/model/:keyword?', label: t('breadcrumbs.models'), pid: 1, id: 3 },
  { path: '/home/dataset/:keyword?', label: t('breadcrumbs.datasets'), pid: 1, id: 4 },
  { path: '/home/task/filter/:ids?', label: t('breadcrumbs.task.filter'), pid: 2, id: 6 },
  { path: '/home/task/train/:ids?', label: t('breadcrumbs.task.training'), pid: 2, id: 7 },
  { path: '/home/task/label/:id?', label: t('breadcrumbs.task.label'), pid: 2, id: 8 },
  { path: '/home/task/mining/:ids?', label: t('breadcrumbs.task.mining'), pid: 2, id: 9 },
  { path: '/home/task/detail/:id', label: t('breadcrumbs.task'), pid: 2, id: 10 },
  { path: '/home/dataset/detail/:id', label: t('breadcrumbs.dataset'), pid: 4, id: 13 },
  { path: '/home/model/detail/:id', label: t('breadcrumbs.model'), pid: 3, id: 16 },
  { path: '/home/model/verify/:id', label: t('breadcrumbs.model.verify'), pid: 16, id: 17 },
  { path: '/home/history/:type/:id', label: t('breadcrumbs.history'), pid: 1, id: 18 },
  { path: '/home/keyword', label: t('breadcrumbs.keyword'), pid: 1, id: 19 },
  { path: '/home/configure', label: t('breadcrumbs.configure'), pid: 1, id: 20 },
  { path: '/home/permission', label: t('breadcrumbs.configure.permission'), pid: 20, id: 21 },
  { path: '/home/dataset/add/:id?', label: t('breadcrumbs.dataset.add'), pid: 4, id: 22 },
  { path: '/home/user', label: t('breadcrumbs.user.info'), pid: 1, id: 23 },
  { path: '/home/image', label: t('breadcrumbs.images'), pid: 1, id: 24 },
  { path: '/home/image/detail/:id', label: t('breadcrumbs.image'), pid: 24, id: 25 },
  { path: '/home/image/add/:id?', label: t('breadcrumbs.image.add'), pid: 24, id: 26 },
]

function getCrumbItems(path, crumbs) {
  const crumb = crumbs.find(crumb => crumb.path === path)
  if (!(crumb && crumb.id)) {
    return []
  }
  return loop(crumb.id, crumbs)
}

function loop(id = 1, crumbs) {
  const current = crumbs.find(crumb => crumb.id === id)
  if (current.pid > 0) {
    return [...loop(current.pid, crumbs), current]
  } else {
    return [current]
  }
}

function Breadcrumbs({ suffix = '', titles = {} }) {
  const { path } = useRouteMatch()
  const params = useParams() || {}
  const crumbs = getCrumbs()
  const crumbItems = getCrumbItems(path, crumbs)
  return <div className={s.breadcrumb}>
    <Breadcrumb className={s.breadcrumbContent} separator='/'>
      {crumbItems.map((crumb, index) => {
        const last = index === crumbItems.length - 1
        const link = crumb.path.replace(/:([^\/]+)/m, (str, key) => {
          return params[key] ? params[key] : ''
        })
        const label = titles[index] ? titles[index] : crumb.label
        return <Item key={crumb.path}>
          {last ? <span>{label} {suffix}</span> : <Link to={link}>{label}</Link>}
        </Item>
      })}
    </Breadcrumb>
  </div>
}

export default Breadcrumbs
