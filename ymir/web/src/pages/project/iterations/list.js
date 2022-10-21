import React, { useEffect, useState } from "react"
import { Table, Popover, } from "antd"
import { useSelector } from 'umi'

import t from "@/utils/t"
import { percent, isNumber } from '@/utils/number'
import useFetch from '@/hooks/useFetch'
import { validModel } from '@/constants/model'
import { validDataset } from '@/constants/dataset'

import SampleRates from "@/components/dataset/sampleRates"
import MiningSampleRates from "@/components/dataset/miningSampleRates"

import s from "./index.less"
import StateTag from "@/components/task/stateTag"

function List({ project }) {
  const [iterations, getIterations] = useFetch('iteration/getIterations', [])
  const [list, setList] = useState([])
  const datasets = useSelector(({ dataset }) => dataset.dataset)
  const models = useSelector(({ model }) => model.model)

  useEffect(() => {
    project?.id && getIterations({ id: project.id, more: true })
  }, [project])

  useEffect(() => {
    setList(iterations.length ? fetchHandle(iterations) : [])
  }, [iterations, datasets, models])

  const columns = [
    {
      title: showTitle("iteration.column.round"),
      dataIndex: "round",
      render: (round) => (t('iteration.round.label', { round })),
    },
    {
      title: showTitle("iteration.column.premining"),
      dataIndex: "miningDatasetLabel",
      render: (label, { id, versionName, miningSet }) => renderPop(label, datasets[miningSet], <MiningSampleRates iid={id} />),
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.mining"),
      dataIndex: "miningResultDatasetLabel",
      render: (label, { miningResult }) => renderPop(label, datasets[miningResult]),
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.label"),
      dataIndex: "labelDatasetLabel",
      render: (label, { labelSet }) => renderPop(label, datasets[labelSet]),
      align: 'center',
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.test"),
      dataIndex: "testDatasetLabel",
      render: (label, { testSet }) => renderPop(label, datasets[testSet]),
      align: 'center',
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.merging"),
      dataIndex: "trainUpdateDatasetLabel",
      render: (label, { trainEffect, trainUpdateSet }) => renderPop(label, datasets[trainUpdateSet],
        null, <span className={s.extraTag}>{renderExtra(trainEffect)}</span>),
      align: 'center',
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.training"),
      dataIndex: 'map',
      render: (map, { model, mapEffect }) => {
        const md = models[model] || {}
        const label = <>{md.name} {md.versionName} {!validModel(md) ? <StateTag mode='text' state={md.state} /> : null}</>
        return validModel(md) ? <div className={s.td}>
          <span style={{ display: 'inline-block', width: '70%', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {label}
          </span>
          <span>{map >= 0 ? percent(map) : null}</span>
          <span className={s.extraTag}>{renderExtra(mapEffect, true)}</span>
        </div> : null
      },
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
    const iters = iterations.reverse().map(iteration => {
      const {
        trainUpdateSet,
        miningSet,
        miningResult,
        labelSet,
        testSet,
        model,
      } = iteration
      return {
        ...iteration,
        index: `${iteration.id}${new Date().getTime()}`,
        trainUpdateDatasetLabel: renderDatasetLabel(datasets[trainUpdateSet]),
        miningDatasetLabel: renderDatasetLabel(datasets[miningSet]),
        miningResultDatasetLabel: renderDatasetLabel(datasets[miningResult]),
        labelDatasetLabel: renderDatasetLabel(datasets[labelSet]),
        testDatasetLabel: renderDatasetLabel(datasets[testSet]),
        map: models[model]?.map,
      }
    })
    iters.reduce((prev, current) => {
      const prevMap = prev.map || 0
      const currentMap = current.map || 0
      const validModels = prev.model && current.model
      current.mapEffect = validModels ? (currentMap - prevMap) : null

      const validTrainSet = prev.trainUpdateSet && current.trainUpdateSet
      const prevUpdatedTrainSetCount = datasets[prev.trainUpdateSet]?.assetCount || 0
      const currentUpdatedTrainSetCount = datasets[current.trainUpdateSet]?.assetCount || 0
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
    return <span title={label}>
      {label}
      {!validDataset(dataset) ? <StateTag mode='text' state={dataset.state} /> : null}
    </span>
  }

  function showTitle(str) {
    return <strong>{t(str)}</strong>
  }

  return (
    <div className={s.list}>
      <Table
        dataSource={list}
        pagination={false}
        rowKey={(record) => record.index}
        columns={columns}
      ></Table>
    </div>
  )
}

export default List
