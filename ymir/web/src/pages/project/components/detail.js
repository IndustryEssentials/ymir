import React, {  } from "react"
import { Col, Popover, Row, Space } from "antd"
import { Link } from "umi"

import t from "@/utils/t"
import { getStageLabel } from '@/constants/project'
import Iteration from './iteration'

import s from "../detail.less"
import Prepare from "./prepare"
import KeywordRates from "@/components/dataset/keywordRates"
import { EditIcon, SearchEyeIcon, EyeOffIcon } from "@/components/common/icons"

function ProjectDetail({ project = {}, iterations = {}, fresh = () => { } }) {
  const id = project.id


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

  return <>
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
          <Link to={`/home/project/${id}/add`}><EditIcon /><span>{t('project.settings.title')}</span></Link>
          <Link to={`/home/project/${id}/iterations`}><SearchEyeIcon /><span>{t('breadcrumbs.project.iterations')}</span></Link>
          <Link to={`/home/project/${id}/hidden`}><EyeOffIcon /><span>{t('common.hidden.list')}</span></Link>
        </Space>
      </Col>
    </Row>
    {project.round > 0 ?
      <Iteration project={project} iterations={iterations} fresh={fresh} /> : <Prepare project={project} iterations={iterations} fresh={fresh} />}
    <Row className={s.setsPanel} gutter={0} align='middle' style={{ textAlign: 'center' }}>
      {renderProjectDatasetLabel()}
    </Row>
  </>
}
export default ProjectDetail
