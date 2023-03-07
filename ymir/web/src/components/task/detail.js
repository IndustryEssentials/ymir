import React, { useEffect, useState } from 'react'
import { Link, useHistory, useParams, useSelector } from 'umi'
import { Col, Descriptions, Row, Space, Tag } from 'antd'

import t from '@/utils/t'
import { format } from '@/utils/date'
import { getTensorboardLink } from '@/constants/common'
import { TASKTYPES, getTaskTypeLabel } from '@/constants/task'
import useFetch from '@/hooks/useFetch'

import renderLiveCodeItem from '@/components/task/items/livecode'
import VersionName from '@/components/result/VersionName'
import ModelVersionName from '@/components/result/ModelVersionName'
import ImageName from '@/components/image/ImageName'

const { Item } = Descriptions

function TaskDetail({ task = {} }) {
  const { id: pid } = useParams()
  const [dids, setDatasetIds] = useState([])
  const datasets = useSelector(({ dataset }) => dataset.dataset)
  const [_, getDatasets] = useFetch('dataset/batchLocalDatasets')

  useEffect(() => {
    if (!task?.id) {
      return
    }
    const pa = task.parameters || {}
    if (pa) {
      const inds = pa.include_datasets || []
      const exds = pa.exclude_datasets || []
      const ids = [pa.dataset_id, pa.validation_dataset_id, ...inds, ...exds].filter((d) => d)
      if (!ids.length) {
        return
      }
      setDatasetIds(ids)
    }
  }, [task.id])

  useEffect(() => {
    dids.length && getDatasets({ pid, ids: dids })
  }, [dids])

  const labelStyle = {
    width: '15%',
    paddingRight: '20px',
    justifyContent: 'flex-end',
  }

  function hasValidModel(type) {
    return [TASKTYPES.TRAINING, TASKTYPES.MINING, TASKTYPES.INFERENCE].includes(type)
  }

  function isImport(type) {
    return [TASKTYPES.MODELCOPY, TASKTYPES.MODELIMPORT].includes(type)
  }

  function renderDatasetName(id) {
    const ds = datasets[id]
    return (
      <Link key={id} to={`/home/project/${task.project_id}/dataset/${id}`}>
        <VersionName result={ds} />
      </Link>
    )
  }
  function renderDatasetNames(dts = []) {
    return <Space>{dts.map((id) => renderDatasetName(id))}</Space>
  }

  function renderModel(id, pid, label = 'task.mining.form.model.label') {
    return id ? (
      <Item label={t(label)}>
        <Link to={`/home/project/${pid}/model/${id}`}>
          <ModelVersionName id={id} />
        </Link>
      </Item>
    ) : null
  }

  function renderDuration(label) {
    return label ? <Item label={t('task.column.duration')}>{label}</Item> : null
  }

  function renderKeepAnnotations(type) {
    const maps = { 1: 'gt', 2: 'pred' }
    const label = type ? maps[type] : 'none'
    return t(`task.label.form.keep_anno.${label}`)
  }

  function renderPreProcess(preprocess) {
    return preprocess ? (
      <Item label={t('task.train.preprocess.title')} span={2}>
        {Object.keys(preprocess).map((key) => (
          <Row key={key} wrap={false}>
            <Col flex={'200px'} style={{ fontWeight: 'bold' }}>
              {key}:
            </Col>
            <Col flex={1}>{JSON.stringify(preprocess[key])}</Col>
          </Row>
        ))}
      </Item>
    ) : null
  }

  function renderConfig(config = '') {
    const conf = config ? JSON.parse(config) : {}
    return (
      <Item label={t('task.train.form.hyperparam.label')} span={2}>
        {Object.keys(conf).map((key) => (
          <Row key={key} wrap={false}>
            <Col flex={'200px'} style={{ fontWeight: 'bold' }}>
              {key}:
            </Col>
            <Col flex={1}>{conf[key].toString()}</Col>
          </Row>
        ))}
      </Item>
    )
  }

  function renderImage(imageName, span = 1, label = 'task.detail.label.training.image') {
    return (
      <Item label={t(label)} span={span}>
        {imageName}
      </Item>
    )
  }

  function renderImageById(id, span, label) {
    return renderImage(<ImageName id={id} />, span, label)
  }

  function renderImageByUrl(url, span, label) {
    return url ? renderImage(<ImageName url={url} />, span, label) : null
  }

  function renderDatasetSource(id) {
    return <Item label={t('task.origin.dataset')}>{renderDatasetName(id)}</Item>
  }

  function renderImportSource(pa = {}) {
    const label = pa.input_url || pa.input_path || pa.input_group_name || pa.input_dataset_name
    return label ? <Item label={t('task.origin.dataset')}>{label}</Item> : null
  }

  function renderCreateTime(time) {
    return <Item label={t('task.detail.label.create_time')}>{format(time)}</Item>
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

  const renderSys = () => <Item label={t('dataset.column.source')}>{t('task.detail.source.sys')}</Item>
  const renderTraining = () => (
    <>
      <Item label={t('task.train.form.trainsets.label')}>{renderDatasetName(task.parameters.dataset_id)}</Item>
      {renderCreateTime(task.create_datetime)}
      <Item label={t('task.train.form.testsets.label')}>{renderDatasetName(task.parameters.validation_dataset_id)}</Item>
      {renderModel(task.parameters.model_id, task.project_id, 'task.detail.label.premodel')}
      {renderDuration(task.durationLabel)}
      {renderLiveCodeItem(task.config)}
      {renderImageById(task?.parameters?.docker_image_id, 2)}
      <Item label={t('task.detail.label.processing')} span={2}>
        <Link target="_blank" to={getTensorboardLink(task.hash)}>
          {t('task.detail.tensorboard.link.label')}
        </Link>
      </Item>
      {renderPreProcess(task.parameters?.preprocess)}
      {renderConfig(task.parameters?.docker_image_config)}
    </>
  )
  const renderMining = () => (
    <>
      {renderDatasetSource(task?.parameters.dataset_id)}
      {renderCreateTime(task.create_datetime)}
      {renderModel(task.parameters.model_id, task.project_id)}
      <Item label={t('task.mining.form.algo.label')}>{task.parameters.mining_algorithm}</Item>
      <Item label={t('task.mining.form.label.label')}>{task.parameters.generate_annotations ? t('common.yes') : t('common.no')}</Item>
      <Item label={t('task.mining.form.topk.label')}>{task.parameters.top_k}</Item>
      {renderImageById(task?.parameters?.docker_image_id, 2, 'task.detail.label.mining.image')}
      {renderLiveCodeItem(task.config)}
      {renderConfig(task.parameters?.docker_image_config)}
    </>
  )
  const renderLabel = () => (
    <>
      {renderDatasetSource(task?.parameters.dataset_id)}
      {renderCreateTime(task.create_datetime)}
      <Item label={t('task.label.form.member')}>
        {task.parameters.labellers.map((m) => (
          <Tag key={m}>{m}</Tag>
        ))}
      </Item>
      <Item label={t('task.label.form.target.label')}>
        {task.parameters?.keywords?.map((keyword) => (
          <Tag key={keyword}>{keyword}</Tag>
        ))}
      </Item>
      <Item label={t('task.label.form.keep_anno.label')}>
        {renderKeepAnnotations(task.parameters.annotation_type)}
      </Item>
      <Item label={t('task.label.form.desc.label')}>
        {task.parameters.extra_url ? (
          <a target="_blank" href={task.parameters.extra_url}>
            {t('task.detail.label.download.btn')}
          </a>
        ) : null}
      </Item>
    </>
  )
  const renderModelImport = () => (
    <>
      <Item label={t('dataset.column.source')}>{t('task.type.modelimport')}</Item>
      {renderCreateTime(task.create_datetime)}
      {renderImageByUrl(task?.parameters?.docker_image, 2)}
      {renderConfig(task.parameters?.docker_image_config)}
    </>
  )
  const renderModelCopy = () => (
    <>
      <Item label={t('dataset.column.source')}>{t('task.type.modelcopy')}</Item>
      {renderCreateTime(task.create_datetime)}
      {renderModel(task.parameters.model_id, task.project_id, 'task.detail.label.premodel')}
      {renderLiveCodeItem(task.config)}
      {renderImageById(task?.parameters?.docker_image_id, 2)}
      {renderPreProcess(task.parameters?.preprocess)}
      {renderConfig(task.parameters?.docker_image_config)}
    </>
  )
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
      <Item label={t('task.mining.form.model.label')}>
        <Link to={`/home/project/${task.project_id}/model/${task.parameters.model_id}`}>
          <ModelVersionName id={task.parameters.model_id} />
        </Link>
      </Item>
      <Item label={t('task.mining.form.algo.label')}>{task.parameters.mining_algorithm}</Item>
      <Item label={t('task.mining.form.topk.label')}>{task.parameters.top_k}</Item>
      {renderImageById(task?.parameters?.docker_image_id, 1, 'task.inference.form.image.label')}
      {renderLiveCodeItem(task.config)}
      {renderConfig(task.parameters?.docker_image_config)}
    </>
  )
  const renderFusion = () => (
    <>
      {renderDatasetSource(task?.parameters?.dataset_id)}
      {renderCreateTime(task.create_datetime)}
      <Item label={t('task.detail.include_datasets.label')}>{renderDatasetNames(task?.parameters?.include_datasets)}</Item>
      <Item label={t('task.detail.exclude_datasets.label')}>{renderDatasetNames(task?.parameters?.exclude_datasets)}</Item>
      <Item label={t('task.detail.include_labels.label')}>
        {task.parameters?.include_labels?.map((keyword) => (
          <Tag key={keyword}>{keyword}</Tag>
        ))}
      </Item>
      <Item label={t('task.detail.exclude_labels.label')}>
        {task.parameters?.exclude_labels?.map((keyword) => (
          <Tag key={keyword}>{keyword}</Tag>
        ))}
      </Item>
      <Item label={t('task.detail.samples.label')} span={2}>
        {task?.parameters?.sampling_count}
      </Item>
    </>
  )
  const renderMerge = () => (
    <>
      <Item label={t('task.detail.include_datasets.label')} span={2}>{renderDatasetNames(task?.parameters?.include_datasets)}</Item>
      <Item label={t('task.detail.exclude_datasets.label')} span={2}>{renderDatasetNames(task?.parameters?.exclude_datasets)}</Item>
      {renderCreateTime(task.create_datetime)}
    </>
  )
  const renderFilter = () => (
    <>
      {renderDatasetSource(task?.parameters?.dataset_id)}
      {renderCreateTime(task.create_datetime)}
      <Item label={t('task.detail.include_labels.label')}>
        {task.parameters?.include_keywords?.map((keyword) => (
          <Tag key={keyword}>{keyword}</Tag>
        ))}
      </Item>
      <Item label={t('task.detail.exclude_labels.label')}>
        {task.parameters?.exclude_keywords?.map((keyword) => (
          <Tag key={keyword}>{keyword}</Tag>
        ))}
      </Item>
      <Item label={t('task.detail.samples.label')} span={2}>
        {task?.parameters?.sampling_count}
      </Item>
    </>
  )
  return task.id ? (
    <div className="taskDetail">
      <Descriptions
        column={2}
        bordered
        labelStyle={labelStyle}
        title={<div className="title">{t('dataset.column.source') + ' > ' + t(getTaskTypeLabel(task.type))}</div>}
        className="infoTable"
      >
        {task.id ? renderTypes() : null}
      </Descriptions>
    </div>
  ) : null
}

export default TaskDetail
