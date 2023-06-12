import { Card, CardProps } from 'antd'
import { FC, useState, useEffect, ReactNode } from 'react'
import { useHistory, useSelector } from 'umi'
import t from '@/utils/t'
import Breadcrumbs from '@/components/common/breadcrumb'
import DatasetInfer from './components/DatasetInfer'
import SingleInfer from './components/SingleInfer'
import TabKey from './components/TabKey'
import useRequest from '@/hooks/useRequest'
type Props = {}

const dynmicContent = () => {
  const Content: FC<{ type: string; url?: string }> = ({ type, url }) => {
    const Comp = {
      [TabKey.Single]: SingleInfer,
      [TabKey.Dataset]: DatasetInfer,
    }[type]
    return Comp ? <Comp url={url} /> : null
  }
  return Content
}
const InferencePage: FC<Props> = ({}) => {
  const history = useHistory<{ type: string; url?: string }>()
  const [active, setActive] = useState<TabKey>(TabKey.Single)
  const [url, setUrl] = useState<string>()

  const tabs = [
    { key: TabKey.Single, tab: t('llmm.tabs.single') },
    // { key: TabKey.Dataset, tab: t('llmm.tabs.dataset') },
  ]
  const Content = dynmicContent()
  useRequest('image/getGroundedSAMImage', {
    loading: false,
    manual: false,
  })

  useEffect(() => {
    const type = history.location.state?.type as TabKey | undefined
    setActive(type || TabKey.Single)
  }, [history.location.state?.type])

  useEffect(() => {
    history.location.state?.url && setUrl(history.location.state.url)
  }, [history.location.state?.url])

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
        <Content type={active} url={url} />
      </Card>
    </div>
  )
}

export default InferencePage
