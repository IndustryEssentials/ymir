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
import { TASKTYPES } from "@/constants/task"
import s from "./detail.less"
import renderLiveCodeItem from '@/components/task/items/livecode'

const { Item } = Descriptions

function TaskDetail({ task = {}, batchDatasets, getModel }) {
  const history = useHistory()
  const id = task.id
  const [datasets, setDatasets] = useState({})
  const [model, setModel] = useState({})

  useEffect(() => {
    task.id && !isImport(task.type) && fetchDatasets()
    hasValidModel(task.type) && task?.parameters?.model_id && fetchModel(task.parameters.model_id)
  }, [task.id])

  async function fetchDatasets() {
    const pa = task.parameters || {}
    const inds = pa.include_datasets || []
    const exds = pa.exclude_datasets || []
    const ids = [
      pa.dataset_id,
      pa.validation_dataset_id,
      pa.main_dataset_id,
      ...inds,
      ...exds,
    ].filter((d) => d)
    if (!ids.length) {
      return
    }
    const dss = await batchDatasets(ids)
    const names = {}
    dss.forEach((ds) => (names[ds.id] = ds))
    setDatasets(names)
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

  function hasValidModel(type) {
    return [TASKTYPES.TRAINING, TASKTYPES.MINING, TASKTYPES.INFERENCE].includes(type)
  }

  function isImport(type) {
    return [TASKTYPES.MODELCOPY, TASKTYPES.MODELIMPORT].includes(type)
  }

  function renderDatasetName(id) {
    const ds = datasets[id]
    const name = ds ? `${ds.name} ${ds.versionName}` : id
    return (
      <Link key={id} to={`/home/project/${task.project_id}/dataset/${id}`}>
        {name}
      </Link>
    )
  }
  function renderDatasetNames(dts = []) {
    return <Space>{dts.map((id) => renderDatasetName(id))}</Space>
  }

  function renderModel(id, pid, model = {}, label = 'task.mining.form.model.label') {
    return id ? <Item label={t(label)}>
      <Link to={`/home/project/${pid}/model/${id}`}>
        {model?.name || id}
      </Link>
    </Item> : null
  }

  function renderDuration(label) {
    return label ? <Item label={t('task.column.duration')}>{label}</Item> : null
  }

  function renderPreProcess(preprocess) {
    return preprocess ? <Item label={t("task.train.preprocess.title")} span={2}>
      {Object.keys(preprocess).map((key) => (
        <Row key={key} wrap={false}>
          <Col flex={"200px"} style={{ fontWeight: "bold" }}>
            {key}:
          </Col>
          <Col flex={1}>{JSON.stringify(preprocess[key])}</Col>
        </Row>
      ))}
    </Item> : null
  }

  function renderConfig(config = {}) {
    return <Item label={t("task.train.form.hyperparam.label")} span={2}>{
      Object.keys(config).map((key) => (
        <Row key={key} wrap={false}>
          <Col flex={"200px"} style={{ fontWeight: "bold" }}>
            {key}:
          </Col>
          <Col flex={1}>{config[key].toString()}</Col>
        </Row>
      ))
    }</Item>
  }

  function renderTrainImage(image, span = 1) {
    return <Item label={t("task.detail.label.training.image")} span={span}>
      {image}
    </Item>
  }

  function renderDatasetSource(id) {
    return <Item label={t("task.origin.dataset")}>{renderDatasetName(id)}</Item>
  }

  function renderImportSource(pa = {}) {
    return <Item label={t("task.origin.dataset")}>{pa.input_url || pa.input_path || pa.input_group_name || pa.input_dataset_name}</Item>
  }

  function renderCreateTime(time) {
    return (
      <Item label={t("task.detail.label.create_time")}>{format(time)}</Item>
    )
  }

  function renderTypes() {
    const maps = {
      [TASKTYPES.TRAINING]: renderTraining,
      [TASKTYPES.MINING]: renderMining,
      [TASKTYPES.LABEL]: renderLabel,
      [TASKTYPES.IMPORT]: renderImport,
      [TASKTYPES.COPY]: renderCopy,
      [TASKTYPES.INFERENCE]: renderInference,
      [TASKTYPES.FUSION]: renderFusion,
      [TASKTYPES.MERGE]: renderMerge,
      [TASKTYPES.FILTER]: renderFilter,
      [TASKTYPES.MODELCOPY]: renderModelCopy,
      [TASKTYPES.MODELIMPORT]: renderModelImport,
      [TASKTYPES.SYS]: renderSys,
    }
    return maps[task.type]()
  }

  const renderSys = () => <Item label={t("dataset.column.source")}>{t('task.detail.source.sys')}</Item>
  const renderTraining = () => (
    <>
      <Item label={t("task.train.form.trainsets.label")}>
        {renderDatasetName(task.parameters.dataset_id)}
      </Item>
      {renderCreateTime(task.create_datetime)}
      <Item label={t("task.train.form.testsets.label")}>
        {renderDatasetName(task.parameters.validation_dataset_id)}
      </Item>
      {renderModel(task.parameters.model_id, task.project_id, model, 'task.detail.label.premodel')}
      {renderDuration(task.durationLabel)}
      {renderLiveCodeItem(task.config)}
      {renderTrainImage(task?.parameters?.docker_image, 2)}
      <Item label={t("task.detail.label.processing")} span={2}>
        <Link target="_blank" to={getTensorboardLink(task.hash)}>
          {t("task.detail.tensorboard.link.label")}
        </Link>
      </Item>
      {renderPreProcess(task.parameters?.preprocess)}
      {renderConfig(task.config)}
    </>
  )
  const renderMining = () => (
    <>
      {renderDatasetSource(task?.parameters.dataset_id)}
      {renderCreateTime(task.create_datetime)}
      {renderModel(task.parameters.model_id, task.project_id, model)}
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
      {renderLiveCodeItem(task.config)}
      {renderConfig(task.config)}
    </>
  )
  const renderLabel = () => (
    <>
      {renderDatasetSource(task?.parameters.dataset_id)}
      {renderCreateTime(task.create_datetime)}
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
  const renderModelImport = () => <>
    <Item label={t("dataset.column.source")}>{t('task.type.modelimport')}</Item>
    {renderCreateTime(task.create_datetime)}
    {renderTrainImage(task?.parameters?.docker_image, 2)}
    {renderConfig(task.config)}
  </>
  const renderModelCopy = () => <>
    <Item label={t("dataset.column.source")}>{t('task.type.modelcopy')}</Item>
    {renderCreateTime(task.create_datetime)}
    {renderModel(task.parameters.model_id, task.project_id, model, 'task.detail.label.premodel')}
    {renderLiveCodeItem(task.config)}
    {renderTrainImage(task?.parameters?.docker_image, 2)}
    {renderPreProcess(task.parameters?.preprocess)}
    {renderConfig(task.config)}
  </>
  const renderImport = () => (
    <>
      {renderImportSource(task?.parameters)}
      {renderCreateTime(task.create_datetime)}
    </>
  )
  const renderCopy = () => (
    <>
      {renderImportSource(task?.parameters)}
      {renderCreateTime(task.create_datetime)}
    </>
  )
  const renderInference = () => (
    <>
      {renderDatasetSource(task?.parameters.dataset_id)}
      {renderCreateTime(task.create_datetime)}
      <Item label={t("task.mining.form.model.label")}>
        <Link to={`/home/project/${task.project_id}/model/${task.parameters.model_id}`}>
          {model?.name || task.parameters.model_id}
        </Link>
      </Item>
      <Item label={t("task.mining.form.algo.label")}>
        {task.parameters.mining_algorithm}
      </Item>
      <Item label={t("task.mining.form.topk.label")}>
        {task.parameters.top_k}
      </Item>
      <Item label={t("task.inference.form.image.label")}>
        {task.parameters.docker_image}
      </Item>
      {renderLiveCodeItem(task.config)}
      {renderConfig(task.config)}
    </>
  )
  const renderFusion = () => (
    <>
      {renderDatasetSource(task?.parameters?.main_dataset_id)}
      {renderCreateTime(task.create_datetime)}
      <Item label={t("task.detail.include_datasets.label")}>
        {renderDatasetNames(task?.parameters?.include_datasets)}
      </Item>
      <Item label={t("task.detail.exclude_datasets.label")}>
        {renderDatasetNames(task?.parameters?.exclude_datasets)}
      </Item>
      <Item label={t("task.detail.include_labels.label")}>
        {task.parameters?.include_labels?.map((keyword) => (
          <Tag key={keyword}>{keyword}</Tag>
        ))}
      </Item>
      <Item label={t("task.detail.exclude_labels.label")}>
        {task.parameters?.exclude_labels?.map((keyword) => (
          <Tag key={keyword}>{keyword}</Tag>
        ))}
      </Item>
      <Item label={t("task.detail.samples.label")} span={2}>
        {task?.parameters?.sampling_count}
      </Item>
    </>
  )
  const renderMerge = () => (
    <>
      {renderDatasetSource(task?.parameters?.dataset_id)}
      {renderCreateTime(task.create_datetime)}
      <Item label={t("task.detail.include_datasets.label")}>
        {renderDatasetNames(task?.parameters?.include_datasets)}
      </Item>
      <Item label={t("task.detail.exclude_datasets.label")}>
        {renderDatasetNames(task?.parameters?.exclude_datasets)}
      </Item>
    </>
  )
  const renderFilter = () => (
    <>
      {renderDatasetSource(task?.parameters?.dataset_id)}
      {renderCreateTime(task.create_datetime)}
      <Item label={t("task.detail.include_labels.label")}>
        {task.parameters?.include_keywords?.map((keyword) => (
          <Tag key={keyword}>{keyword}</Tag>
        ))}
      </Item>
      <Item label={t("task.detail.exclude_labels.label")}>
        {task.parameters?.exclude_keywords?.map((keyword) => (
          <Tag key={keyword}>{keyword}</Tag>
        ))}
      </Item>
      <Item label={t("task.detail.samples.label")} span={2}>
        {task?.parameters?.sampling_count}
      </Item>
    </>
  )

  return (
    <div className='taskDetail'>
      <Descriptions
        column={2}
        bordered
        labelStyle={labelStyle}
        title={<div className='title'>{t("dataset.column.source")}</div>}
        className='infoTable'
      >
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
    getModel(id, force) {
      return dispatch({
        type: "model/getModel",
        payload: { id, force },
      })
    },
  }
}

export default connect(props, actions)(TaskDetail)
