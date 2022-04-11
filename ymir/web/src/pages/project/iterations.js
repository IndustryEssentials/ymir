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
      render: (label, { versionName, miningDataset }) => renderPop(label, miningDataset),
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.mining"),
      dataIndex: "miningResultDatasetLabel",
      render: (label, { miningResultDataset }) => renderPop(label, miningResultDataset),
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.label"),
      dataIndex: "labelDatasetLabel",
      render: (label, { labelDataset }) => renderPop(label, labelDataset),
      align: 'center',
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.merging"),
      dataIndex: "trainUpdateDatasetLabel",
      render: (label, { trainEffect, trainUpdateDataset }) => renderPop(label, trainUpdateDataset,
        <span className={s.extraTag}>{renderExtra(trainEffect)}</span>),
      align: 'center',
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.training"),
      dataIndex: "trainingModelLabel",
      render: (map, { mapEffect }) => <div className={s.td}>
        <span>{percent(map)}</span>
        <span className={s.extraTag}>{renderExtra(mapEffect, true)}</span>
      </div>,
      align: 'center',
    },
  ]

  function renderPop(label, dataset = {}, extra) {
    dataset.project = project
    const content = <KeywordRates dataset={dataset} progressWidth={0.6}></KeywordRates>
    return <Popover content={content} overlayInnerStyle={{ minWidth: 500 }}>
      {/* <div className={s.td}> */}
        <span>{label}</span>
        {extra}
      {/* </div> */}
    </Popover>
  }

  function renderExtra(value, showPercent = false) {
    const cls = value < 0 ? s.negative : s.positive
    const label = showPercent ? percent(value) : value
    return value ? <span className={cls}>{label}</span> : null
  }

  async function fetchIterations() {
    const result = await func.getIterations(id)
    if (result) {
      const iters = fetchHandle(result)
      console.log('fetch iteration iters:', iters)
      setIterations(iters)
    }
  }

  async function fetchProject() {
    const result = await func.getProject(id)
    result && setProject(result)
  }

  function fetchHandle(iterations) {
    const iters = iterations.map(iteration => {
      return {
        ...iteration,
        trainUpdateDatasetLabel: renderDatasetLabel(iteration.trainUpdateDataset),
        miningDatasetLabel: renderDatasetLabel(iteration.miningDataset),
        miningResultDatasetLabel: renderDatasetLabel(iteration.miningResultDataset),
        labelDatasetLabel: renderDatasetLabel(iteration.labelDataset),
        trainingModelLabel: renderModelLabel(iteration.trainingModel),
      }
    })
    console.log('iters:', JSON.parse(JSON.stringify(iters)))
    iters.reduce((prev, current) => {
      const prevMap = prev.map || 0
      const prevUpdatedTrainSetCount = prev?.trainUpdateDataset?.assetCount || 0
      const currentMap = current.map
      const currentUpdatedTrainSetCount = current?.trainUpdateDataset?.assetCount || 0
      current.mapEffect = prevMap ? (currentMap - prevMap) : 0
      current.trainEffect = prevUpdatedTrainSetCount ? (currentUpdatedTrainSetCount - prevUpdatedTrainSetCount) : 0
      return current
    }, {})
    return iters
  }

  function renderDatasetLabel(dataset) {
    return dataset ? `${dataset.name} ${dataset.versionName} (${dataset.assetCount})` : ''
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
          <Table
            dataSource={iterations}
            pagination={false}
            columns={columns}
          ></Table>
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
