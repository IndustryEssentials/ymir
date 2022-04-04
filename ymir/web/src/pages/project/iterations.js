import React, { useEffect, useState } from "react"
import { connect } from 'dva'
import s from "./index.less"
import { useHistory, useParams } from "umi"
import { Form, Table, Modal, ConfigProvider, Card, Space, Row, Col, Button, Popover, } from "antd"

import t from "@/utils/t"
import { percent } from '@/utils/number'
import Breadcrumbs from "@/components/common/breadcrumb"
import EmptyState from '@/components/empty/model'
import KeywordRates from "@/components/dataset/keywordRates"

function Iterations({ ...func }) {
  const history = useHistory()
  const { id } = useParams()
  const [project, setProject] = useState({})
  const [iterations, setIterations] = useState([])

  useEffect(() => {
    if (id) {
      fetchIterations()
      fetchProject()
    }
  }, [id])

  const columns = [
    {
      title: showTitle("iteration.column.round"),
      dataIndex: "round",
      render: (round) => (t('iteration.round.label', { round })),
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.premining"),
      dataIndex: "miningDatasetLabel",
      render: (label, { miningDataset }) => renderPop(label, miningDataset),
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.mining"),
      dataIndex: "miningResultDatasetLabel",
      render: (label, { miningResultDataset }) => renderPop(label, miningResultDataset),
    },
    {
      title: showTitle("iteration.column.label"),
      dataIndex: "labelDatasetLabel",
      render: (label, { labelDataset }) => renderPop(label, labelDataset),
      align: 'center',
    },
    {
      title: showTitle("iteration.column.merging"),
      dataIndex: "trainUpdateDatasetLabel",
      render: (label, { trainUpdateDataset }) => renderPop(label, trainUpdateDataset),
      align: 'center',
    },
    {
      title: showTitle("iteration.column.training"),
      dataIndex: "trainingModelLabel",
      align: 'center',
    },
  ]

  function renderPop(label, dataset = {}) {
    dataset.project = project
    const content = <KeywordRates dataset={dataset} progressWidth={0.6}></KeywordRates>
    return <Popover content={content} overlayInnerStyle={{ minWidth: 400 }}>
      <span>{label}</span>
    </Popover>
  }

  async function fetchIterations() {
    const result = await func.getIterations(id)
    console.log('result: ', result)
    if (result) {
      const iters = result.map(i => {
        return {
          ...i,
          trainUpdateDatasetLabel: renderDatasetLabel(i.trainUpdateDataset),
          miningDatasetLabel: renderDatasetLabel(i.miningDataset),
          miningResultDatasetLabel: renderDatasetLabel(i.miningResultDataset),
          labelDatasetLabel: renderDatasetLabel(i.labelDataset),
          trainingModelLabel: renderModelLabel(i.trainingModel),
        }
      })
      setIterations(iters)
    }
  }

  async function fetchProject() {
    const result = await func.getProject(id)
    console.log('project: ', result)
    result && setProject(result)
  }

  function renderDatasetLabel(dataset) {
    return dataset ? `${dataset.name} (${dataset.assetCount})` : ''
  }

  function renderModelLabel(model) {
    return model ? `${model.name} ${model.versionName} | ${percent(model.map)}` : ''
  }

  function showTitle(str) {
    return <strong>{t(str)}</strong>
  }

  function renderTitle() {
    return (
      <Row>
        <Col flex={1}>{project.name} {t('project.iterations.title')}</Col>
        <Col><Button type='link' onClick={() => history.goBack()}>{t('common.back')}&gt;</Button></Col>
      </Row>
    )
  }

  return (
    <div className={s.iterations}>
      <Breadcrumbs />
      <Card title={renderTitle()}>
        <Space className={s.detailPanel}>
          <span>{t('project.train_classes')}: {project?.keywords?.join(',')}</span>
          <span className={s.iterationInfo}>{t('project.detail.info.iteration', { current: project.round, target: project.targetIteration })}</span>
          {project.targetMap ? <span>{t('project.target.map')}: {project.targetMap}%</span> : null}
          {project.targetDataset ? <span>{t('project.target.dataset')}: {project.targetDataset}</span> : null}
          {project.description ? <span>{t('project.detail.desc')}: {project.description}</span> : null}
        </Space>
        <div className={s.table}>
          <ConfigProvider renderEmpty={() => <EmptyState />}>
            <Table
              dataSource={iterations}
              pagination={false}
              columns={columns}
            ></Table>
          </ConfigProvider>
        </div>
      </Card>
    </div>
  )
}

const props = (state) => {
  return {
    logined: state.user.logined,
  }
}

const actions = (dispatch) => {
  return {
    getProject(id) {
      return dispatch({
        type: "project/getProject",
        payload: { id },
      })
    },
    getIterations(id) {
      return dispatch({
        type: 'iteration/getIterations',
        payload: { id, more: true },
      })
    }
  }
}

export default connect(props, actions)(Iterations)
