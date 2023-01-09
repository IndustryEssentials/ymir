import React, { useEffect } from 'react'
import { Button, Card, Col, Row, Space } from 'antd'
import { useParams, useHistory } from 'umi'

import t from '@/utils/t'
import useFetch from '@/hooks/useFetch'
import Breadcrumbs from '@/components/common/breadcrumb'
import Empty from '@/components/empty/default'
import { getStepLabel } from '@/constants/iteration'
import Detail from '@/components/project/Detail'
import Name from '@/components/search/Name'

import s from './detail.less'
import { TrainIcon, NavDatasetIcon, ArrowRightIcon, ImportIcon } from '@/components/common/Icons'

function ProjectDetail(func) {
  const history = useHistory()
  const { id } = useParams()
  const [project, getProject] = useFetch('project/getProject', {})

  useEffect(() => {
    id && getProject({ id, force: true })
  }, [id])

  const title = (Icon, label) => (
    <div className={s.cardTitle}>
      <Icon className={s.titleIcon} />
      <span className={s.titleLabel}>{t(label)}</span>
    </div>
  )

  function add() {
    history.push(`/home/project/${id}/dataset/add`)
  }

  function goTraining() {
    history.push(`/home/project/${id}/train`)
  }

  const statBlocks = (blocks = []) => blocks.map((block, index) => <Col key={index} span={24 / blocks.length}>{statBlock(block)}</Col>)

  const statBlock = ({ label, count }) => (
    <>
      <div className="contentLabel">{t(label)}</div>
      <div className={s.num}>{count}</div>
    </>
  )

  function search(name) {
    history.push(`/home/project/${id}/search`, { name })
  }

  return (
    <div>
      <Breadcrumbs />
      <Detail project={project} />
      {project.enableIteration ? (
        <div className={s.header}>
          {project.round > 0 ? (
            <div>
              <span style={{ marginRight: 20 }}>
                {t('project.iteration.entrance.status', {
                  stateLabel: <span className="orange">{t(getStepLabel(project.currentStep, project.round))}</span>,
                })}
              </span>
              <Button type="primary" onClick={() => history.push(`/home/project/${id}/iterations`)}>
                <TrainIcon />
                {t('project.iteration.entrance.btn')}
              </Button>
            </div>
          ) : (
            <div style={{ textAlign: 'center' }}>
              <Empty description={t('project.iteration.entrance.empty.label')} />
              <p>{t('project.iteration.entrance.empty.info')}</p>
              <Button type="primary" onClick={() => history.push(`/home/project/${id}/iterations`)}>
                <TrainIcon /> {t('project.iteration.entrance.empty.btn')}
              </Button>
            </div>
          )}
        </div>
      ) : null}
      
      <div className="actions">
        <Row gutter={10}>
          <Col flex={1}>
            <Name onSearch={search} enterButton={t('common.search')} />
          </Col>
          <Col>
            <Button type="primary" onClick={add}>
              <ImportIcon /> {t('dataset.import.label')}
            </Button>
          </Col>
          <Col>
            <Button type="primary" onClick={goTraining}>
              <TrainIcon /> {t('project.iteration.stage.training')}
            </Button>
          </Col>
        </Row>
      </div>
      <div className={`list ${s.projectOverview}`}>
        <Row gutter={10}>
          <Col span={12}>
            <Card
              title={title(NavDatasetIcon, 'project.tab.set.title')}
              className={s.cardContainer}
              onClick={() => {
                history.push(`/home/project/${project.id}/dataset`)
              }}
              extra={<ArrowRightIcon className={s.rightIcon} />}
            >
              <Row className="content" justify="center">
                {statBlocks([
                  { label: 'project.stats.datasets.total', count: project.datasetCount },
                  { label: 'project.stats.datasets.processing', count: project.datasetProcessingCount },
                  { label: 'project.stats.datasets.invalid', count: project.datasetErrorCount },
                  { label: 'project.stats.datasets.assets.total', count: project.totalAssetCount },
                ])}
              </Row>
            </Card>
          </Col>
          <Col span={12}>
            <Card
              title={title(TrainIcon, 'project.tab.model.title')}
              className={s.cardContainer}
              onClick={() => {
                history.push(`/home/project/${project.id}/model`)
              }}
              extra={<ArrowRightIcon className={s.rightIcon} />}
            >
              <Row className="content" justify="center">
                {statBlocks([
                  { label: 'project.stats.models.total', count: project.modelCount },
                  { label: 'project.stats.models.processing', count: project.modelProcessingCount },
                  { label: 'project.stats.models.invalid', count: project.modelErrorCount },
                ])}
              </Row>
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  )
}

export default ProjectDetail
