import React, { useEffect, useState } from "react"
import { Card } from "antd"
import { useLocation, useParams, useHistory } from "umi"

import t from "@/utils/t"
import useFetch from "@/hooks/useFetch"
import Breadcrumbs from "@/components/common/breadcrumb"

import Analysis from "./diagnose/analysis"
import Metrics from "./diagnose/metrics"
import Training from "./diagnose/training"
import Visualization from "./diagnose/visualization"

import s from "./detail.less"

const tabs = [
  { tab: 'model.diagnose.tab.analysis', key: 'analysis', },
  { tab: 'model.diagnose.tab.metrics', key: 'metrics', },
  { tab: 'model.diagnose.tab.training', key: 'training', },
  { tab: 'model.diagnose.tab.visualization', key: 'visualization', },

]

function ProjectDetail() {
  const history = useHistory()
  const location = useLocation()
  const { id } = useParams()
  const [active, setActive] = useState(tabs[0].key)
  const [project, fetchProject] = useFetch('project/getProject')
  const content = {
    [tabs[0].key]: <Analysis pid={id} project={project} />,
    [tabs[1].key]: <Metrics pid={id} project={project} />,
    [tabs[2].key]: <Training pid={id} project={project} />,
    [tabs[3].key]: <Visualization pid={id} project={project} />,
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
      <Card tabList={tabs.map(tab => ({ ...tab, tab: t(tab.tab) }))}
        activeTabKey={active} onTabChange={tabChange} className='noShadow'
        headStyle={{ background: '#fff', marginBottom: '10px' }}
        bodyStyle={{ padding: '0 20px' }}>
        {content[active]}
      </Card>
    </div>
  )
}

export default ProjectDetail
