import React, { useEffect, useState } from "react"
import { Table, Popover } from "antd"
import { useSelector } from "umi"

import t from "@/utils/t"
import { percent, isNumber } from "@/utils/number"
import useFetch from "@/hooks/useFetch"
import { validModel } from "@/constants/model"
import { validDataset } from "@/constants/dataset"
import { STEP } from "@/constants/iteration"

import SampleRates from "@/components/dataset/SampleRates"
import MiningSampleRates from "@/components/dataset/miningSampleRates"
import Dataset from "@/components/form/option/Dataset"
import VersionName from "@/components/result/VersionName"

import s from "./index.less"
import StateTag from "@/components/task/StateTag"

function List({ project }) {
  const [iterations, getIterations] = useFetch("iteration/getIterations", [])
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
      render: (round) => t("iteration.round.label", { round }),
    },
    {
      title: showTitle("iteration.column.premining"),
      dataIndex: STEP.prepareMining,
      render: (ds, { id }) => renderPop(ds, <MiningSampleRates iid={id} />),
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.mining"),
      dataIndex: STEP.mining,
      render: (ds) => renderPop(ds),
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.label"),
      dataIndex: STEP.labelling,
      render: (ds) => renderPop(ds),
      align: "center",
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.test"),
      dataIndex: "testDatasetLabel",
      render: (_, { testSet }) => renderPop(testSet),
      align: "center",
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.merging"),
      dataIndex: STEP.merging,
      render: (ds, { trainEffect }) =>
        renderPop(
          ds,
          null,
          <span className={s.extraTag}>{renderExtra(trainEffect)}</span>
        ),
      align: "center",
      ellipsis: true,
    },
    {
      title: showTitle("iteration.column.training"),
      dataIndex: STEP.training,
      render: (id, { mapEffect }) => {
        const md = models[id]
        if (!md) {
          return
        }
        const map = md.map || 0
        const label = (
          <>
            <VersionName result={md} />
            {!validModel(md) ? <StateTag mode="text" state={md.state} /> : null}
          </>
        )
        return validModel(md) ? (
          <div className={s.td}>
            <span
              style={{
                display: "inline-block",
                width: "70%",
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}
            >
              {label}
            </span>
            <span>{map >= 0 ? percent(map) : null}</span>
            <span className={s.extraTag}>{renderExtra(mapEffect, true)}</span>
          </div>
        ) : null
      },
      align: "center",
    },
  ]

  function renderPop(id, ccontent, extra = "") {
    const dataset = datasets[id]
    if (!dataset) {
      return
    }
    dataset.project = project
    const label = renderDatasetLabel(dataset)
    const content = ccontent || (
      <SampleRates
        label={label}
        keywords={project.keywords}
        dataset={dataset}
        progressWidth={0.4}
      />
    )
    return (
      <Popover content={content} overlayInnerStyle={{ minWidth: 500 }}>
        <span title={label}>{label}</span>
        {extra}
      </Popover>
    )
  }

  function renderExtra(value, showPercent = false) {
    const cls = value < 0 ? s.negative : value > 0 ? s.positive : s.neutral
    const label = showPercent ? percent(value) : value
    return isNumber(value) ? <span className={cls}>{label}</span> : null
  }

  function fetchHandle(iterations) {
    const iters = iterations.map((iteration) => {
      const iterationDatas = iteration.steps.reduce(
        (prev, step) => ({
          ...prev,
          [step.name]: step.resultId,
        }),
        {}
      )
      return {
        ...iteration,
        index: `${iteration.id}${new Date().getTime()}`,
        ...iterationDatas,
      }
    })
    return iters
      .map((current, index) => {
        const prev = iters[index - 1]
        const mapEffect = getMapEffect(prev, current)
        const trainEffect = getDatasetDiff(prev, current)
        return {
          ...current,
          mapEffect,
          trainEffect,
        }
      })
      .reverse()
  }

  function getMapEffect(prev, step) {
    if (!prev) {
      return
    }
    const prevModel = models[prev[STEP.training]]
    const currentModel = models[step[STEP.training]]
    const prevMap = prevModel?.map || 0
    const map = currentModel?.map || 0
    return map - prevMap
  }

  function getDatasetDiff(prev, step) {
    if (!prev) {
      return
    }
    const prevDataset = datasets[prev[STEP.merging]]
    const currentDataset = datasets[step[STEP.merging]]
    const prevCount = prevDataset?.assetCount || 0
    const currentCount = currentDataset?.assetCount || 0
    return currentCount - prevCount
  }

  function renderDatasetLabel(dataset) {
    if (!dataset) {
      return
    }
    const label = `${dataset.name} ${dataset.versionName} (${dataset.assetCount})`
    return (
      <span title={label}>
        <Dataset dataset={dataset} />
        {!validDataset(dataset) ? (
          <StateTag mode="text" state={dataset.state} />
        ) : null}
      </span>
    )
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
