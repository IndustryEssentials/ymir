import React, { useEffect, useRef, useState } from "react"
import { connect } from "dva"
import { Link, useHistory } from "umi"
import {
  Button,
  Card,
  Col,
  Descriptions,
  Progress,
  Row,
  Space,
  Tag,
} from "antd"

import t from "@/utils/t"
import { format } from "@/utils/date"
import { getTensorboardLink } from "@/services/common"
import Terminate from "./terminate"
import { TASKTYPES } from "@/constants/task"
import s from "./detail.less"
import IgnoreKeywords from "../common/ignoreKeywords"

const { Item } = Descriptions

function TaskDetail({ task = {}, ignore = [], batchDatasets, getModel }) {
  const history = useHistory()
  const id = task.id
  const [datasetNames, setDatasetNames] = useState({})
  const [model, setModel] = useState({})

  useEffect(() => {
    task.id && fetchDatasets()
    task?.parameters?.model_id && fetchModel(task.parameters.model_id)
  }, [task.id])

  async function fetchDatasets() {
    const pa = task.parameters || {}
    const ids = (pa ? [pa.dataset_id, pa.validation_dataset_id]
      : [pa.dataset_id]).filter(d => d)
    if (!ids.length) {
      return
    }
    const dss = await batchDatasets(ids)
    const names = {}
    dss.forEach((ds) => (names[ds.id] = ds))
    setDatasetNames(names)
  }

  async function fetchModel(id) {
    const result = await getModel(id)

    result && setModel(result)
  }

  const labelStyle = {
    width: "15%",
    paddingRight: "20px",
    justifyContent: "flex-end",
  }

  function renderDatasetName(id) {
    const ds = datasetNames[id]
    const name = ds ? `${ds.name} ${ds.versionName}` : ''
    return (
      <Link key={id} to={`/home/dataset/detail/${id}`}>
        {name || id}
      </Link>
    )
  }
  function renderDatasetNames(dts = []) {
    return <Space>{dts.map((id) => renderDatasetName(id))}</Space>
  }

  function renderConfig(config = {}) {
    return Object.keys(config).map((key) => (
      <Row key={key} wrap={false}>
        <Col flex={"200px"} style={{ fontWeight: "bold" }}>
          {key}:
        </Col>
        <Col flex={1}>{config[key]}</Col>
      </Row>
    ))
  }

  function renderTypes() {
    const maps = {
      [TASKTYPES.TRAINING]: renderTraining,
      [TASKTYPES.MINING]: renderMining,
      [TASKTYPES.LABEL]: renderLabel,
      [TASKTYPES.IMPORT]: renderImport,
      [TASKTYPES.COPY]: renderImport,
      [TASKTYPES.INFERENCE]: renderInference,
      [TASKTYPES.FUSION]: renderFusion,
    }
    return maps[task.type]()
  }

  const renderTraining = () => (
    <>
      {console.log(task, "task")}
      <Item label={t("task.train.form.trainsets.label")}>
        {renderDatasetName(task.parameters.dataset_id)}
      </Item>
      <Item label={t("task.train.form.testsets.label")}>
        {renderDatasetName(task.parameters.validation_dataset_id)}
      </Item>
      <Item label={t("task.detail.label.train_goal")}>
        {task?.parameters?.keywords?.map((keyword) => (
          <Tag key={keyword}>{keyword}</Tag>
        ))}
      </Item>
      <Item label={t("task.detail.label.framework")}>
        {task.parameters?.network}
      </Item>
      <Item label={t("task.detail.label.create_time")}>
        {format(task.create_datetime)}
      </Item>
      <Item label={t("task.detail.label.backbone")}>
        {task.parameters?.backbone}
      </Item>
      <Item label={t("task.detail.label.training.image")}>
        {task?.parameters?.docker_image}
      </Item>
      <Item label={t("task.mining.form.model.label")}>
        {task?.parameters?.model_id ? (
          <Link to={`/home/model/detail/${task.parameters.model_id}`}>
            {task?.model?.name || task.parameters.model_id}
          </Link>
        ) : null}
      </Item>
      <Item label={t("task.detail.label.hyperparams")} span={2}>
        {renderConfig(task.config)}
      </Item>
      <Item label={"TensorBoard"} span={2}>
        <Link target="_blank" to={getTensorboardLink(task.hash)}>
          {t("task.detail.tensorboard.link.label")}
        </Link>
      </Item>
    </>
  )
  const renderMining = () => (
    <>
      <Item label={t("task.mining.form.model.label")}>
        <Link to={`/home/model/detail/${task.parameters.model_id}`}>
          {model?.name || task.parameters.model_id}
        </Link>
      </Item>
      <Item label={t("task.mining.form.algo.label")}>
        {task.parameters.mining_algorithm}
      </Item>
      <Item label={t("task.mining.form.label.label")}>
        {task.parameters.generate_annotations
          ? t("common.yes")
          : t("common.no")}
      </Item>
      <Item label={t("task.mining.form.topk.label")}>
        {task.parameters.top_k}
      </Item>
      <Item label={t("task.detail.label.mining.image")} span={2}>
        {task.parameters.docker_image}
      </Item>
      <Item label={t("task.detail.label.hyperparams")} span={2}>
        {renderConfig(task.config)}
      </Item>
    </>
  )
  const renderLabel = () => (
    <>
      <Item label={t("task.label.form.member")}>
        {task.parameters.labellers.map((m) => (
          <Tag key={m}>{m}</Tag>
        ))}
      </Item>
      <Item label={t("task.label.form.target.label")}>
        {task.parameters?.keywords?.map((keyword) => (
          <Tag key={keyword}>{keyword}</Tag>
        ))}
      </Item>
      <Item label={t("task.label.form.keep_anno.label")}>
        {task.parameters.keep_annotations ? t("common.yes") : t("common.no")}
      </Item>
      <Item label={t("task.label.form.desc.label")}>
        {task.parameters.extra_url ? (
          <a target="_blank" href={task.parameters.extra_url}>
            {t("task.detail.label.download.btn")}
          </a>
        ) : null}
      </Item>
    </>
  )
  const renderImport = () => (
    <>
      <Item label={t("dataset.column.ignored_keyword")}>
        <IgnoreKeywords keywords={ignore} />
      </Item>
    </>
  )
  const renderInference = () => <></>
  const renderFusion = () => <></>

  return (
    <div className={s.taskDetail}>
      <Descriptions
        column={2}
        bordered
        labelStyle={labelStyle}
        title={<div className={s.title}>{t("dataset.column.source")}</div>}
        className={s.infoTable}
      >
        <Item label={t("task.origin.dataset")}>
          {renderDatasetName(task?.parameters?.dataset_id)}
        </Item>
        <Item label={t("task.detail.label.create_time")}>
          {format(task.create_datetime)}
        </Item>
        {task.id ? renderTypes() : null}
      </Descriptions>
    </div>
  )
}

const props = (state) => {
  return {
    logined: state.user.logined,
    taskItem: state.task.task,
  }
}

const actions = (dispatch) => {
  return {
    batchDatasets(ids) {
      return dispatch({
        type: "dataset/batchDatasets",
        payload: ids,
      })
    },
    getModel(id) {
      return dispatch({
        type: "model/getModel",
        payload: id,
      })
    },
  }
}

export default connect(props, actions)(TaskDetail)
