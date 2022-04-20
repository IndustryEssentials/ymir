import React, { useCallback, useEffect, useState } from "react"
import { Card, Col, Row, Space } from "antd"
import { useLocation, useParams, connect, Link, useHistory } from "umi"

import t from "@/utils/t"
import { percent } from '@/utils/number'
import Breadcrumbs from "@/components/common/breadcrumb"
import Iteration from './components/iteration'
import Datasets from '@/components/dataset/list'
import Models from '@/components/model/list'

import s from "./detail.less"
import Prepare from "./components/prepare"

const tabsTitle = [
  { tab: t('project.tab.set.title'), key: 'set', },
  { tab: t('project.tab.model.title'), key: 'model', },
]

function ProjectDetail(func) {
  const history = useHistory()
  const location = useLocation()
  const { id } = useParams()
  const [project, setProject] = useState({})
  const [active, setActive] = useState(tabsTitle[0].key)
  const content = {
    'set': <Datasets pid={id} project={project} />,
    'model': <Models pid={id} project={project} />
  }

  useEffect(() => {
    id && fetchProject(true)
  }, [id])

  useEffect(() => {
    const locationHash = location.hash.replace(/^#/, '')
    // if (locationHash) {
      setActive(locationHash || tabsTitle[0].key)
    // }
  }, [location.hash])

  async function fetchProject(force) {
    const result = await func.getProject(id, force)
    if (result) {
      setProject(result)
    }
  }
  const fresh = useCallback(() => {
    fetchProject(true)
  }, [])

  function tabChange(key) {
    history.push(`#${key}`)
  }

  return (
    <div className={s.projectDetail}>
      <Breadcrumbs />
      <div className={s.header}>
        <Row>
          <Col flex={1}>
            <Space className={s.detailPanel}>
              <span className={s.name}>{project.name}</span>
              <span className={s.iterationInfo}>
                {t('project.detail.info.iteration', { 
                  current: <span className={s.orange}>{project.round}</span>, 
                  target: <span className={s.orange}>{project.targetIteration}</span> 
                })}
              </span>
              <span>{t('project.train_classes')}: <span className={s.bold}>{project?.keywords?.join(',')}</span></span>
              {project.targetMap ? <span>{t('project.target.map')}: <span className={s.target}>{project.targetMap}%</span></span> : null}
              {project.targetDataset ? <span>{t('project.target.dataset')}: <span className={s.target}>{project.targetDataset}</span></span> : null}
              {project.description ? <span>{t('project.detail.desc')}: {project.description}</span> : null}
            </Space>
          </Col>
          <Col>
            <Space>
              <Link to={`/home/project/add/${id}`}>{t('breadcrumbs.project.add')}</Link>
              <Link to={`/home/project/iterations/${id}`}>{t('breadcrumbs.project.iterations')}</Link>
            </Space>
          </Col>
        </Row>
        {project.round > 0 ?
          <Iteration project={project} fresh={fresh} /> : <Prepare project={project} fresh={fresh} />}
      </div>
      <Card tabList={tabsTitle} activeTabKey={active} onTabChange={tabChange}
        style={{ margin: '-20px -5vw 0', background: 'transparent' }}
        headStyle={{ padding: '0 5vw', background: '#fff', marginBottom: '20px' }}
        bodyStyle={{ padding: '0 5vw' }}>
        {content[active]}
      </Card>
    </div>
  )
}


const actions = (dispacth) => {
  return {
    getProject(id, force) {
      return dispacth({
        type: 'project/getProject',
        payload: { id, force },
      })
    }
  }
}

export default connect(null, actions)(ProjectDetail)
