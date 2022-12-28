import { Card } from 'antd'
import { FC, useEffect, useState } from 'react'
import { useHistory, useLocation, useParams } from 'umi'

import Breadcrumbs from '@/components/common/breadcrumb'
import t from '@/utils/t'
import DatasetList from './components/DatasetList'
import ModelList from './components/ModelList'

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

  useEffect(() => {
    const type = location.state?.type
    const name = location.state.name
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
