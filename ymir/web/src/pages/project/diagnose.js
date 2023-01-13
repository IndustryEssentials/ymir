import React, { useEffect, useState } from 'react'
import { Card } from 'antd'
import { useLocation, useParams, useHistory } from 'umi'

import t from '@/utils/t'
import useFetch from '@/hooks/useFetch'
import { isDetection } from '@/constants/project'

import Breadcrumbs from '@/components/common/breadcrumb'
import Metrics from './diagnose/metrics'
import Training from './diagnose/training'
import InferDataset from './diagnose/InferDataset'

import s from './detail.less'
const TabsKey = ['infer_datasets', 'metrics', 'training']
const tab = (key) => ({ tab: `model.diagnose.tab.${key}`, key })
const tabs = TabsKey.map((key) => tab(key))

const content = {
  [TabsKey[0]]: InferDataset,
  [TabsKey[1]]: Metrics,
  [TabsKey[2]]: Training,
}
const getTabContent = (key) => () => {
  const Content = content[key]
  return (props) => <Content {...props} />
}

function Diagnose() {
  const history = useHistory()
  const location = useLocation()
  const { id } = useParams()
  const [active, setActive] = useState(tabs[0].key)
  const [TabContent, setTabContent] = useState(getTabContent(TabsKey[0]))
  const [project, fetchProject] = useFetch('project/getProject')

  useEffect(() => {
    id && fetchProject({ id, force: true })
  }, [id])

  useEffect(() => {
    id && active && setTabContent(getTabContent(active))
  }, [active, id])

  useEffect(() => {
    const tabKey = location.hash.replace(/^#/, '')
    setActive(tabKey || tabs[0].key)
  }, [location.hash])

  function tabChange(key) {
    history.push(`#${key}`)
  }

  return (
    <div className={s.projectDetail}>
      <Breadcrumbs />
      <Card
        tabList={tabs.filter((tab) => {
          console.log('tab:', tab, project?.type, TabsKey[1])
          return tab.key !== TabsKey[1] || isDetection(project?.type) 
        }).map((tab) => ({ ...tab, tab: t(tab.tab) }))}
        activeTabKey={active}
        onTabChange={tabChange}
        className="noShadow"
        headStyle={{ background: '#fff', marginBottom: '10px' }}
        bodyStyle={{ padding: '0 20px' }}
      >
        {<TabContent pid={id} project={project} />}
      </Card>
    </div>
  )
}

export default Diagnose
