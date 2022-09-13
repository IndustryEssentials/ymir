import React, { useEffect } from "react"
import { Button, Card, Col, Row, Space } from "antd"
import { useParams, useHistory } from "umi"

import t from "@/utils/t"
import useFetch from '@/hooks/useFetch'
import Breadcrumbs from "@/components/common/breadcrumb"
import Empty from "@/components/empty/default"
import { getStageLabel } from '@/constants/project'

import s from "./detail.less"
import { TrainIcon, NavDatasetIcon, ArrowRightIcon, ImportIcon } from "@/components/common/icons"

function ProjectDetail(func) {
  const history = useHistory()
  const { id } = useParams()
  const [project, getProject] = useFetch('project/getProject', {})

  useEffect(() => {
    id && getProject({ id, force: true })
  }, [id])

  const title = (Icon, label) => <div className={s.cardTitle}>
    <Icon className={s.titleIcon} />
    <span className={s.titleLabel}>{t(label)}</span>
  </div>

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
        {project.round > 0 ? <div>
          <span style={{ marginRight: 20 }}>{t('project.iteration.entrance.status', {
            stateLabel: <span className='orange'>{t(getStageLabel(project.currentStage, project.round))}</span>
          })}</span>
          <Button type="primary" onClick={() => history.push(`/home/project/${id}/iterations`)}><TrainIcon />{t('project.iteration.entrance.btn')}</Button>
        </div> :
          <div style={{ textAlign: 'center' }}>
            <Empty description={t('project.iteration.entrance.empty.label')} />
            <p>{t('project.iteration.entrance.empty.info')}</p>
            <Button type="primary" onClick={() => history.push(`/home/project/${id}/iterations`)}>
              <TrainIcon /> {t('project.iteration.entrance.empty.btn')}
              </Button>
          </div>}
      </div>
      <Space className="actions">
        <Button type="primary" onClick={add}><ImportIcon /> {t("dataset.import.label")}</Button>
        <Button type="primary" onClick={goTraining}><TrainIcon /> {t("project.iteration.stage.training")}</Button>
      </Space>
      <div className={`list ${s.projectOverview}`}>
        <Row gutter={10}>
          <Col span={12}>
            <Card title={title(NavDatasetIcon, 'project.tab.set.title')} className={s.cardContainer}
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
            <Card title={title(TrainIcon, 'project.tab.model.title')} className={s.cardContainer}
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

export default ProjectDetail
