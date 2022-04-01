import React, { useEffect, useState } from "react"
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

const taskTypes = ["fusion", "train", "mining", "label"]

function DatasetDetail({ getDataset }) {
  const history = useHistory()
  const { id } = useParams()
  const [dataset, setDataset] = useState({})

  useEffect(() => {
    fetchDataset()
  }, [id])

  async function fetchDataset() {
    const result = await getDataset(id)
    if (result) {
      setDataset(result)
    }
  }

  return (
    <div>
      <Breadcrumbs />
      <Card
        title={t("dataset.detail.title") + ">" + t(getTaskTypeLabel(dataset.taskType))}
        className={s.datasetDetail}
      >
        <Detail dataset={dataset} />
        <TaskProgress state={dataset.state} task={dataset.task} duration={dataset.durationLabel} progress={dataset.progress} />
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
          {taskTypes.map((type) => (
            <Button
              key={type}
              type="primary"
              onClick={() => history.push(`/home/task/${type}/${id}`)}
            >
              {t(`task.type.${type}`)}
            </Button>
          ))}
        </Space>
      </Card>
    </div>
  )
}

const actions = (dispatch) => {
  return {
    getDataset: (id) => {
      return dispatch({
        type: "dataset/getDataset",
        payload: id,
      })
    },
  }
}

export default connect(null, actions)(DatasetDetail)
