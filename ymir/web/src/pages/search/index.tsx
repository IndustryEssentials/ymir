import { Card } from 'antd'
import { FC, useEffect, useState } from 'react'
import { useHistory, useLocation, useParams } from 'umi'

import Breadcrumbs from '@/components/common/breadcrumb'
import t from '@/utils/t'
import DatasetList from './components/DatasetList'
import ModelList from './components/ModelList'

type Props = {}

const tabsTitle = [
  { tab: t('project.tab.set.title'), key: 'dataset' },
  { tab: t('project.tab.model.title'), key: 'model' },
]

const SearchIndex: FC<Props> = ({}) => {
  const history = useHistory()
  const location = useLocation<{ type: string }>()
  const { id } = useParams<{ id: string }>()
  const pid = Number(id)
  const [active, setActive] = useState(tabsTitle[0].key)
  const contents = {
    [tabsTitle[0].key]: <DatasetList pid={pid} />,
    [tabsTitle[1].key]: <ModelList pid={pid} />,
  }

  useEffect(() => {
    const type = location?.state?.type
    if (typeof type !== 'undefined') {
      setActive(type)
    }
  }, [location.state])

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
        {contents[active]}
      </Card>
    </div>
  )
}

export default SearchIndex
