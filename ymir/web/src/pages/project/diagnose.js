import React, { useEffect, useState } from "react"
import { Card } from "antd"
import { useLocation, useParams, useHistory } from "umi"

import t from "@/utils/t"
import useFetch from "@/hooks/useFetch"
import Breadcrumbs from "@/components/common/breadcrumb"

import Metrics from "./diagnose/metrics"
import Training from "./diagnose/training"
import InferDataset from './diagnose/InferDataset'

import s from "./detail.less"
const TabsKey = ['infer_datasets', 'metrics', 'training']
const tab = key => ({ tab: `model.diagnose.tab.${key}`, key })
const tabs = TabsKey.map(key => tab(key))

function ProjectDetail() {
  const history = useHistory()
  const location = useLocation()
  const { id } = useParams()
  const [active, setActive] = useState(tabs[0].key)
  const [project, fetchProject] = useFetch('project/getProject')
  const content = {
    [TabsKey[0]]: <InferDataset pid={id} />,
    [TabsKey[1]]: <Metrics pid={id} project={project} />,
    [TabsKey[2]]: <Training pid={id} project={project} />,
  }

  useEffect(() => {
    id && fetchProject({ id, force: true })
  }, [id])

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
      <Card tabList={tabs.filter(tab => !tab.hidden).map(tab => ({ ...tab, tab: t(tab.tab) }))}
        activeTabKey={active} onTabChange={tabChange} className='noShadow'
        headStyle={{ background: '#fff', marginBottom: '10px' }}
        bodyStyle={{ padding: '0 20px' }}>
        {content[active]}
      </Card>
    </div>
  )
}

export default ProjectDetail
