import React, { useEffect, useRef, useState } from "react"
import { connect } from "dva"
import { useHistory, useParams, Link } from "umi"
import { Button, Card, Space } from "antd"

import t from "@/utils/t"
import { TASKTYPES, getTaskTypeLabel } from "@/constants/task"
import Breadcrumbs from "@/components/common/breadcrumb"
import TaskDetail from "@/components/task/detail"
import Detail from "@/components/dataset/detail"
import s from "./detail.less"
import TaskProgress from "@/components/task/progress"
import Error from "@/components/task/error"
import Hide from "@/components/common/hide"
import useRestore from "@/hooks/useRestore"

const taskTypes = ["fusion", "train", "mining", "label", 'inference', 'copy']

function DatasetDetail({ datasetCache, getDataset }) {
  const history = useHistory()
  const { id: pid, did: id } = useParams()
  const [dataset, setDataset] = useState({})
  const hideRef = useRef(null)
  const restoreAction = useRestore(pid)

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

  async function fetchDataset(force) {
    await getDataset(id, force)
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
        title={t("dataset.detail.title") + ">" + t(getTaskTypeLabel(dataset.taskType))}
      >
        <div className={s.content}>
          <Detail dataset={dataset} />
          <TaskProgress state={dataset.state} result={dataset} task={dataset.task} duration={dataset.durationLabel} progress={dataset.progress} fresh={() => fetchDataset(true)} />
          {dataset?.task?.error_code ? <Error code={dataset.task?.error_code} msg={dataset.task?.error_message} /> : null}
          <TaskDetail
            task={dataset.task}
            ignore={dataset.ignoredKeywords}
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
              {taskTypes.map((type) => (
                <Button
                  key={type}
                  type="primary"
                  onClick={() => history.push(`/home/task/${type}/${pid}?did=${id}`)}
                >
                  {t(`task.type.${type}`)}
                </Button>
              ))}
              <Button type="primary" onClick={() => hide(dataset)}>
                {t(`common.action.hide`)}
              </Button>
              <Button type="primary" onClick={() => history.push(`/home/project/${pid}/dataset/${dataset.groupId}/compare/${id}`)}>
                {t(`common.action.compare`)}
              </Button>
            </> :
              <Button type="primary" onClick={restore}>
                {t("common.action.restore")}
              </Button>
            }

          </Space>
        </div>
      </Card>
      <Hide ref={hideRef} ok={hideOk} />
    </div>
  )
}

const props = (state) => {
  return {
    datasetCache: state.dataset.dataset,
  }
}

const actions = (dispatch) => {
  return {
    getDataset: (id, force) => {
      return dispatch({
        type: "dataset/getDataset",
        payload: { id, force },
      })
    },
  }
}

export default connect(props, actions)(DatasetDetail)
