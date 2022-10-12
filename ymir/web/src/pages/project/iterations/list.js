import React, { useEffect, useState } from "react"
import { Table, Popover, } from "antd"

import t from "@/utils/t"
import { percent, isNumber } from '@/utils/number'
import useFetch from '@/hooks/useFetch'
import { validModel } from '@/constants/model'

import SampleRates from "@/components/dataset/sampleRates"
import MiningSampleRates from "@/components/dataset/miningSampleRates"

import s from "./index.less"

function RatesHOC(Rates) {
  function RatesRender(props) {
    return <Rates {...props} />
  }
  return RatesRender
}

function List({ project }) {
  const [iterations, getIterations] = useFetch('iteration/getIterations', [])
  const [list, setList] = useState([])

  useEffect(() => {
    project?.id && getIterations({ id: project.id, more: true })
  }, [project])

  useEffect(() => iterations.length && setList(fetchHandle(iterations)), [iterations])

  const columns = [
    {
      title: showTitle("iteration.column.round"),
      dataIndex: "round",
      render: (round) => (t('iteration.round.label', { round })),
    },
    {
      title: showTitle("iteration.column.premining"),
      dataIndex: "miningDatasetLabel",
      render: (label, { id, versionName, entities }) => renderPop(label, entities?.miningSet, <MiningSampleRates iid={id} />),
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.mining"),
      dataIndex: "miningResultDatasetLabel",
      render: (label, { entities }) => renderPop(label, entities?.miningResult),
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.label"),
      dataIndex: "labelDatasetLabel",
      render: (label, { entities }) => renderPop(label, entities?.labelSet),
      align: 'center',
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.test"),
      dataIndex: "testDatasetLabel",
      render: (label, { entities }) => renderPop(label, entities?.testSet),
      align: 'center',
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.merging"),
      dataIndex: "trainUpdateDatasetLabel",
      render: (label, { trainEffect, entities }) => renderPop(label, entities?.trainUpdateSet,
        null, <span className={s.extraTag}>{renderExtra(trainEffect)}</span>),
      align: 'center',
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.training"),
      dataIndex: 'map',
      render: (map, { entities, mapEffect }) => validModel(entities?.model || {}) ? <div className={s.td}>
        <span style={{ display: 'inline-block', width: '70%', overflow: 'hidden', textOverflow: 'ellipsis'}}>
          {entities?.model?.name}
        </span>
        <span>{map >= 0 ? percent(map) : null}</span>
        <span className={s.extraTag}>{renderExtra(mapEffect, true)}</span>
      </div> : null,
      align: 'center',
    },
  ]

  function renderPop(label, dataset = {}, ccontent, extra = '') {
    dataset.project = project
    const content = ccontent || <SampleRates label={label} keywords={project.keywords} dataset={dataset} progressWidth={0.4} />
    return <Popover content={content} overlayInnerStyle={{ minWidth: 500 }}>
      <span title={label}>{label}</span>
      {extra}
    </Popover>
  }

  function renderExtra(value, showPercent = false) {
    const cls = value < 0 ? s.negative : (value > 0 ? s.positive : s.neutral)
    const label = showPercent ? percent(value) : value
    return isNumber(value) ? <span className={cls}>{label}</span> : null
  }

  function fetchHandle(iterations) {
    const iters = iterations.map(iteration => {
      const {
        trainUpdateSet,
        miningSet,
        miningResult,
        labelSet,
        testSet,
        model,
      } = iteration.entities
      return {
        ...iteration,
        trainUpdateDatasetLabel: renderDatasetLabel(trainUpdateSet),
        miningDatasetLabel: renderDatasetLabel(miningSet),
        miningResultDatasetLabel: renderDatasetLabel(miningResult),
        labelDatasetLabel: renderDatasetLabel(labelSet),
        testDatasetLabel: renderDatasetLabel(testSet),
        map: model?.map,
      }
    })
    iters.reduce((prev, current) => {
      const prevMap = prev.map || 0
      const currentMap = current.map || 0
      const prevEntities = prev?.entities || {}
      const currentEntities = current?.entities || {}
      const validModels = prevEntities.model && currentEntities.model
      current.mapEffect = validModels ? (currentMap - prevMap) : null

      const validTrainSet = prevEntities.trainUpdateSet && currentEntities.trainUpdateSet
      const prevUpdatedTrainSetCount = prevEntities.trainUpdateSet?.assetCount || 0
      const currentUpdatedTrainSetCount = currentEntities.trainUpdateSet?.assetCount || 0
      current.trainEffect = validTrainSet ? (currentUpdatedTrainSetCount - prevUpdatedTrainSetCount) : null

      return current
    }, {})
    return iters
  }

  function renderDatasetLabel(dataset) {
    if (!dataset) {
      return
    }
    const label = `${dataset.name} ${dataset.versionName} (${dataset.assetCount})`
    return <span title={label}>{label}</span>
  }

  function showTitle(str) {
    return <strong>{t(str)}</strong>
  }

  return (
    <div className={s.list}>
      <Table
        dataSource={list}
        pagination={false}
        rowKey={(record) => record.id}
        columns={columns}
      ></Table>
    </div>
  )
}

export default List
