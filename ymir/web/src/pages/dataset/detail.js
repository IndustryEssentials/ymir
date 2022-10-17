import React, { useEffect, useRef, useState } from "react"
import { useHistory, useParams, Link, useSelector } from "umi"
import { Button, Card, message, Space } from "antd"

import t from "@/utils/t"
import { TASKTYPES, getTaskTypeLabel } from "@/constants/task"
import useFetch from '@/hooks/useFetch'
import useRestore from "@/hooks/useRestore"
import { canHide } from '@/constants/dataset'

import Breadcrumbs from "@/components/common/breadcrumb"
import TaskDetail from "@/components/task/detail"
import Detail from "@/components/dataset/detail"
import TaskProgress from "@/components/task/progress"
import Error from "@/components/task/error"
import Hide from "@/components/common/hide"

import s from "./detail.less"
import useRerunAction from "../../hooks/useRerunAction"

const taskTypes = ["merge", "filter", "train", "mining", "label", 'inference', 'copy']

function DatasetDetail() {
  const history = useHistory()
  const { id: pid, did: id } = useParams()
  const [dataset, getDataset, setDataset] = useFetch('dataset/getDataset', {})
  const datasetCache = useSelector(({ dataset }) => dataset.dataset)
  const hideRef = useRef(null)
  const restoreAction = useRestore(pid)
  const generateRerunBtn = useRerunAction('btn')

  useEffect(() => {
    fetchDataset(true)
  }, [id])

  useEffect(() => {
    if (datasetCache[id]?.needReload) {
      fetchDataset(true)
    } else {
      datasetCache[id] && setDataset(datasetCache[id])
    }
  }, [datasetCache])

  function fetchDataset(force) {
    getDataset({ id, verbose: true, force })
  }

  const hide = (version) => {
    if (dataset?.project?.hiddenDatasets?.includes(version.id)) {
      return message.warn(t('dataset.hide.single.invalid'))
    }
    hideRef.current.hide([version])
  }

  const hideOk = () => {
    fetchDataset(true)
  }

  async function restore() {
    const result = await restoreAction('dataset', [id])
    if (result) {
      fetchDataset(true)
    }
  }

  return (
    <div>
      <Breadcrumbs />
      <Card
        title={t("dataset.detail.title")}
      >
        <div className={s.content}>
          <Detail dataset={dataset} />
          <TaskProgress
            state={dataset.state}
            result={dataset}
            task={dataset.task}
            duration={dataset.durationLabel}
            progress={dataset.progress}
            fresh={() => fetchDataset(true)}
          />
          <Error code={dataset.task?.error_code} msg={dataset.task?.error_message} terminated={dataset?.task?.is_terminated} />
          <TaskDetail
            task={dataset.task}
          ></TaskDetail>
          <Space style={{ width: "100%", justifyContent: "flex-end" }}>
            {dataset.taskType === TASKTYPES.LABEL ? (
              <div style={{ textAlign: "right" }}>
                <Link target="_blank" to="/label_tool/">
                  {t("task.detail.label.go.platform")}
                </Link>
              </div>
            ) : null}
            {!dataset.hidden ? <>
              {taskTypes.map((type, index) => index === 0 || dataset.assetCount > 0 ? (
                <Button
                  key={type}
                  type="primary"
                  onClick={() => history.push(`/home/project/${pid}/${type}?did=${id}`)}
                >
                  {t(`common.action.${type}`)}
                </Button>
              ) : null)}
              {canHide(dataset) ? <Button type="primary" onClick={() => hide(dataset)}>
                {t(`common.action.hide`)}
              </Button> : null}
            </> :
              <Button type="primary" onClick={restore}>
                {t("common.action.restore")}
              </Button>
            }
            {generateRerunBtn(dataset)}
          </Space>
        </div>
      </Card>
      <Hide ref={hideRef} ok={hideOk} />
    </div>
  )
}

export default DatasetDetail
