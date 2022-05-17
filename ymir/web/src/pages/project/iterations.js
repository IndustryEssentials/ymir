import React, { useEffect, useState } from "react"
import { connect } from 'dva'
import s from "./index.less"
import { useHistory, useParams } from "umi"
import { Form, Table, Modal, ConfigProvider, Card, Space, Row, Col, Button, Popover, } from "antd"

import t from "@/utils/t"
import { percent, isNumber } from '@/utils/number'
import { getStageLabel } from '@/constants/project'
import Breadcrumbs from "@/components/common/breadcrumb"
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
      title: showTitle("iteration.column.test"),
      dataIndex: "testDatasetLabel",
      render: (label, { testDataset }) => renderPop(label, testDataset),
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
      dataIndex: 'map',
      render: (map, { mapEffect }) => <div className={s.td}>
        <span>{map >= 0 ? percent(map) : null}</span>
        <span className={s.extraTag}>{renderExtra(mapEffect, true)}</span>
      </div>,
      align: 'center',
    },
  ]

  function renderPop(label, dataset = {}, extra) {
    dataset.project = project
    const content = <KeywordRates dataset={dataset} progressWidth={0.4}></KeywordRates>
    return <Popover content={content} overlayInnerStyle={{ minWidth: 500 }}>
      <span>{label}</span>
      {extra}
    </Popover>
  }

  function renderExtra(value, showPercent = false) {
    const cls = value < 0 ? s.negative : (value > 0 ? s.positive : s.neutral)
    const label = showPercent ? percent(value) : value
    return isNumber(value) ? <span className={cls}>{label}</span> : null
  }

  async function fetchIterations() {
    const result = await func.getIterations(id)
    if (result) {
      const iters = fetchHandle(result)
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
        testDatasetLabel: renderDatasetLabel(iteration.testDataset),
        map: iteration?.trainingModel?.map,
      }
    })
    iters.reduce((prev, current) => {
      const prevMap = prev.map || 0
      const currentMap = current.map || 0
      const validModels = prev.trainingModel && current.trainingModel
      current.mapEffect = validModels ? (currentMap - prevMap) : null

      const validTrainSet = prev.trainUpdateDataset && current.trainUpdateDataset
      const prevUpdatedTrainSetCount = prev?.trainUpdateDataset?.assetCount || 0
      const currentUpdatedTrainSetCount = current?.trainUpdateDataset?.assetCount || 0
      current.trainEffect = validTrainSet ? (currentUpdatedTrainSetCount - prevUpdatedTrainSetCount) : null

      return current
    }, {})
    return iters
  }

  function renderDatasetLabel(dataset) {
    return dataset ? `${dataset.name} ${dataset.versionName} (${dataset.assetCount})` : ''
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
          <span className={s.iterationInfo}>
            {t('project.detail.info.iteration', {
              stageLabel: <span className={s.orange}>{t(getStageLabel(project.currentStage, project.round))}</span>,
              current: <span className={s.orange}>{project.round}</span>,
            })}
          </span>
          {project.description ? <span>{t('project.detail.desc')}: {project.description}</span> : null}
        </Space>
        <div className={s.table}>
          <Table
            dataSource={iterations}
            pagination={false}
            rowKey={(record) => record.id}
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
