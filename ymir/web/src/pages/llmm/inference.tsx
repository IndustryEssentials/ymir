import { Card, CardProps } from 'antd'
import { FC, useState, useEffect, ReactNode } from 'react'
import { useHistory, useSelector } from 'umi'
import t from '@/utils/t'
import Breadcrumbs from '@/components/common/breadcrumb'
import DatasetInfer from './components/DatasetInfer'
import SingleInfer from './components/SingleInfer'
import TabKey from './components/TabKey'
type Props = {}

const dynmicContent = () => {
  const Content: FC<{ type: string }> = ({ type }) => {
    const Comp = {
      [TabKey.Single]: SingleInfer,
      [TabKey.Dataset]: DatasetInfer,
    }[type]
    return Comp ? <Comp /> : null
  }
  return Content
}
const inference: FC<Props> = ({}) => {
  const history = useHistory<{ type: string }>()
  const [active, setActive] = useState<TabKey>(TabKey.Single)
  const tabs = [
    { key: TabKey.Single, tab: t('llmm.tabs.single') },
    { key: TabKey.Dataset, tab: t('llmm.tabs.dataset') },
  ]
  const Content = dynmicContent()

  useEffect(() => {
    const type = history.location.state.type as TabKey
    setActive(type || TabKey.Single)
  }, [history.location.state.type])

  return (
    <div>
      <Breadcrumbs />
      <Card
        tabList={tabs}
        activeTabKey={active}
        onTabChange={(key) => {
          history.replace({ state: { type: key } })
        }}
      >
        <Content type={active} />
      </Card>
    </div>
  )
}
export default inference
