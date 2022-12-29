import { Card } from 'antd'
import { FC, useEffect, useState } from 'react'
import { useHistory, useLocation, useParams } from 'umi'
import { useSelector } from 'react-redux'

import Breadcrumbs from '@/components/common/breadcrumb'
import t from '@/utils/t'
import DatasetList from './components/DatasetList'
import ModelList from './components/ModelList'
import Detail from '@/components/project/Detail'
import useRequest from '@/hooks/useRequest'
import Search from './components/Search'

type Props = {
}

const tabsTitle = [
  { tab: t('project.tab.set.title'), key: 'dataset' },
  { tab: t('project.tab.model.title'), key: 'model' },
]

const SearchIndex: FC<Props> = () => {
  const history = useHistory()
  const location = useLocation<{ type?: string; name?: string }>()
  const { id } = useParams<{ id: string }>()
  const pid = Number(id)
  const [active, setActive] = useState(tabsTitle[0].key)
  const [searchName, setSearchName] = useState<string | undefined>('')
  const project = useSelector<YStates.Root, YModels.Project>(({ project }) => project.projects[pid])
  const { run: getProject } = useRequest('project/getProject', {
    loading: false
  })

  useEffect(() => {
    !project && getProject({ id: pid })
  }, [project])

  useEffect(() => {
    const type = location.state?.type
    const name = location.state?.name
    if (typeof type !== 'undefined') {
      setActive(type)
    }
    setSearchName(name)
  }, [location.state])

  const listRender = (active?: string) => {
    const Comp = active !== tabsTitle[0].key ? DatasetList : ModelList
    return <Comp pid={pid} name={searchName} />
  }

  return (
    <div>
      <Breadcrumbs />
      <Detail project={project} />
      <Search />
      <Card
        tabList={tabsTitle}
        activeTabKey={active}
        onTabChange={(key) => {
          history.replace({ state: { type: key } })
        }}
      >
        {listRender(active)}
      </Card>
    </div>
  )
}

export default SearchIndex
