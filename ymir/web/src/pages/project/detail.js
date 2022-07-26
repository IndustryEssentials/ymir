import React, { useCallback, useEffect, useState } from "react"
import { Button, Card, Col, Row, Space } from "antd"
import { useParams, connect, useHistory } from "umi"
import t from "@/utils/t"
import Breadcrumbs from "@/components/common/breadcrumb"
import s from "./detail.less"
import { TrainIcon, NavDatasetIcon, ArrowRightIcon, ImportIcon } from "@/components/common/icons"
import NoIterationDetail from "./components/noIterationDetail"

function ProjectDetail(func) {
  const history = useHistory()
  const { id } = useParams()
  const [iterations, setIterations] = useState([])
  const [project, setProject] = useState({})

  useEffect(() => {
    id && fetchProject(true)
    id && fetchIterations(id)
  }, [id])

  async function fetchProject(force) {
    const result = await func.getProject(id, force)
    if (result) {
      setProject(result)
    }
  }
  const fresh = useCallback(() => {
    fetchProject(true)
  }, [])

  async function fetchIterations(pid) {
    const iterations = await func.getIterations(pid)
    if (iterations) {
      setIterations(iterations)
    }
  }

  function datasetTitle() {
    return <div className={s.cardTitle}><NavDatasetIcon className={s.titleIcon} /><span className={s.titleLabel}>{t('project.tab.set.title')}</span></div>
  }

  function modelTitle() {
    return <div className={s.cardTitle}><TrainIcon className={s.titleIcon} /><span className={s.titleLabel}>{t('project.iteration.stage.training')}</span></div>
  }

  function add() {
    history.push(`/home/project/${id}/dataset/add`)
  }

  function goTraining() {
    history.push(`/home/project/${id}/train`)
  }

  return (
    <div>
      <Breadcrumbs />
      <div className={s.header}>
        <NoIterationDetail project={project} />
      </div>
      <Space className="actions">
        <Button type="primary" onClick={add}><ImportIcon /> {t("dataset.import.label")}</Button>
        <Button type="primary" onClick={goTraining}><TrainIcon /> {t("project.iteration.stage.training")}</Button>
      </Space>
      <div className={`list ${s.projectOverview}`}>
        <Row gutter={10}>
          <Col span={12}>
            <Card title={datasetTitle()} className={s.cardContainer}
              onClick={() => { history.push(`/home/project/${project.id}/dataset`) }}
              extra={<ArrowRightIcon className={s.rightIcon} />}>
              <Row className='content' justify="center">
                <Col span={12}>
                  <div className='contentLabel'>{t('project.tab.set.title')}</div>
                  <div className={s.num}>{project.setCount}</div>
                </Col>
                <Col span={12}>
                  <div className='contentLabel'>{t('project.detail.datavolume')}</div>
                  <div className={`${s.num} ${s.blue}`}>{project.totalAssetCount}</div>
                </Col>
              </Row>
            </Card>
          </Col>
          <Col span={12}>
            <Card title={modelTitle()} className={s.cardContainer}
              onClick={() => { history.push(`/home/project/${project.id}/model`) }}
              extra={<ArrowRightIcon className={s.rightIcon} />}>
              <Row className='content' justify="center">
                <Col span={12}>
                  <div className='contentLabel'>{t('project.tab.model.title')}</div>
                  <div className={s.num}>{project.modelCount}</div>
                </Col>
                <Col span={12}>
                  <div className='contentLabel'>{t('project.detail.runningtasks')}/{t('project.detail.totaltasks')}</div>
                  <div className={s.num}><span className={s.red}></span>{project.runningTaskCount}/{project.totalTaskCount}<span></span></div>
                </Col>
              </Row>
            </Card>
          </Col>
        </Row>

      </div>
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
