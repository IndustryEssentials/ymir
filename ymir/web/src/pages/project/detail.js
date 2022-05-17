import React, { useCallback, useEffect, useState } from "react"
import { Card, Col, Popover, Row, Space } from "antd"
import { useLocation, useParams, connect, Link, useHistory } from "umi"

import t from "@/utils/t"
import { getStageLabel, tabs } from '@/constants/project'
import Breadcrumbs from "@/components/common/breadcrumb"
import Iteration from './components/iteration'
import Datasets from '@/components/dataset/list'
import Models from '@/components/model/list'

import s from "./detail.less"
import Prepare from "./components/prepare"
import KeywordRates from "@/components/dataset/keywordRates"
import { EditIcon, SearchEyeIcon, EyeOffIcon } from "../../components/common/icons"
import CheckProjectDirty from "../../components/common/CheckProjectDirty"

function ProjectDetail(func) {
  const history = useHistory()
  const location = useLocation()
  const { id } = useParams()
  const [iterations, setIterations] = useState([])
  const [group, setGroup] = useState(0)
  const [project, setProject] = useState({})
  const [active, setActive] = useState(tabs[0].key)
  const content = {
    [tabs[0].key]: <Datasets pid={id} project={project} group={group} iterations={iterations} />,
    [tabs[1].key]: <Models pid={id} project={project} group={group} iterations={iterations} />
  }

  useEffect(() => {
    id && fetchProject(true)
    id && fetchIterations(id)
  }, [id])

  useEffect(() => {
    const locationHash = location.hash.replace(/^#/, '')
    const [tabKey, gid] = (locationHash || '').split('_')
    setGroup(gid)
    setActive(tabKey || tabs[0].key)
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

  async function fetchIterations(pid) {
    const iterations = await func.getIterations(pid)
    if (iterations) {
      setIterations(iterations)
    }
  }

  function renderProjectDatasetLabel() {
    const getDsName = (ds = {}) => ds.name ? (ds.name + ' ' + (ds.versionName || '')) : ''
    const maps = [
      { label: 'project.add.form.training.set', name: getDsName(project.trainSet) },
      { dataset: project.testSet, label: 'project.add.form.test.set', name: getDsName(project.testSet) },
      { dataset: project.miningSet, label: 'project.add.form.mining.set', name: getDsName(project.miningSet) },
    ]

    return maps.map(({ name, label, dataset }) => {
      const rlabel = <span>{t(label)}: {name}</span>
      return <Col key={label} className={s.ellipsis} span={8} title={name}>
        {dataset ? renderPop(rlabel, dataset) : rlabel}
      </Col>
    })
  }


  function renderPop(label, dataset = {}) {
    dataset.project = project
    const content = <KeywordRates dataset={dataset} progressWidth={0.4}></KeywordRates>
    return <Popover content={content} overlayInnerStyle={{ minWidth: 500 }}>
      <span>{label}</span>
    </Popover>
  }

  return (
    <div className={s.projectDetail}>
      <Breadcrumbs />
      <div className={s.header}>
        <Row>
          <Col flex={1}>
            <Space className={s.detailPanel} wrap>
              <span className={s.name}>{project.name}</span>
              <span className={s.iterationInfo}>
                {t('project.detail.info.iteration', {
                  stageLabel: <span className={s.orange}>{t(getStageLabel(project.currentStage, project.round))}</span>,
                  current: <span className={s.orange}>{project.round}</span>,
                })}
              </span>
              <span>{t('project.train_classes')}: <span className={s.black}>{project?.keywords?.join(',')}</span></span>
              {project.description ? <span>{t('project.detail.desc')}: {project.description}</span> : null}
            </Space>
          </Col>
          <Col>
            <Space>
              <Link to={`/home/project/add/${id}`}><EditIcon /><span>{t('project.settings.title')}</span></Link>
              <Link to={`/home/project/iterations/${id}`}><SearchEyeIcon /><span>{t('breadcrumbs.project.iterations')}</span></Link>
              <Link to={`/home/project/hidden/${id}`}><EyeOffIcon /><span>{t('common.hidden.list')}</span></Link>
            </Space>
          </Col>
        </Row>
        {project.round > 0 ?
          <Iteration project={project} iterations={iterations} fresh={fresh} /> : <Prepare project={project} iterations={iterations} fresh={fresh} />}
        <Row className={s.setsPanel} gutter={0} align='middle' style={{ textAlign: 'center' }}>
          {renderProjectDatasetLabel()}
        </Row>
      </div>
      <Card tabList={tabs.map(tab => ({ ...tab, tab: t(tab.tab) }))} tabBarExtraContent={<CheckProjectDirty pid={id} />}
        activeTabKey={active} onTabChange={tabChange} className='noShadow'
        style={{ margin: '-20px -5vw 0', background: 'transparent' }}
        headStyle={{ padding: '0 5vw', background: '#fff', marginBottom: '10px' }}
        bodyStyle={{ padding: '0 5vw' }}>
        {content[active]}
      </Card>
    </div>
  )
}


const actions = (dispatch) => {
  return {
    getProject(id, force) {
      return dispatch({
        type: 'project/getProject',
        payload: { id, force },
      })
    },
    getIterations(id) {
      return dispatch({
        type: 'iteration/getIterations',
        payload: { id, },
      })
    },
  }
}

export default connect(null, actions)(ProjectDetail)
