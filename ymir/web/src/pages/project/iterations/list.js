import React, { useEffect, useState } from "react"
import { Table, Popover, } from "antd"

import t from "@/utils/t"
import { percent, isNumber } from '@/utils/number'
import useFetch from '@/hooks/useFetch'

import KeywordRates from "@/components/dataset/keywordRates"

import s from "./index.less"

function List({ project }) {
  const [iterations, getIterations] = useFetch('iteration/getIterations', [])
  const [list, setList] = useState([])

  useEffect(() => {
    console.log('project in list:', project)
    project?.id && getIterations({ id: project.id })
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
    const content = <KeywordRates keywords={project.keywords} dataset={dataset} progressWidth={0.4}></KeywordRates>
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

  function fetchHandle(iterations) {
    console.log('iterations in list:', iterations)
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
