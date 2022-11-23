import { Col, Descriptions, Row, Tag } from 'antd'
import React, { useEffect, useState } from 'react'
import { Link, useSelector } from 'umi'

import t from '@/utils/t'
import { getMergeStrategyLabel, getLabelAnnotationType } from '@/constants/common'
import { STEP } from '@/constants/iteration'
import VersionName from '@/components/result/VersionName'
import ModelVersionName from '@/components/result/ModelVersionName'
import ImageName from '@/components/image/ImageName'

type Props = {
  step: YModels.PageStep
}
type ListType = { label: string; content: any }[]

const FinishStep: React.FC<Props> = ({ step }) => {
  const selected = step?.value
  const result = useSelector((state: any) => {
    if (!selected) {
      return
    }
    const resource = step.resultType && state[step.resultType][step.resultType]
    return step.resultId && resource[step.resultId]
  })
  const [paramsList, setParamsList] = useState<ListType>([])

  useEffect(() => {
    if (!result) {
      return
    }
    const maps: { [key: string]: Function } = {
      [STEP.prepareMining]: getFusionParams,
      [STEP.mining]: getMiningParams,
      [STEP.labelling]: getLabelParams,
      [STEP.merging]: getMergeParams,
      [STEP.training]: getTrainingParams,
    }
    const task = result.task
    const config = task.parameters.docker_image_config ? JSON.parse(task.parameters.docker_image_config) : undefined
    setParamsList([
      ...maps[step.value]({
        ...task.parameters,
        gpuCount: task?.config?.gpu_count,
        config,
      }),
      { label: 'common.desc', content: task.parameters.description },
    ])
  }, [result])

  const renderDescriptions = (list: ListType) => (
    <Descriptions column={2} contentStyle={{ flexWrap: 'wrap' }}>
      {list.map(({ label, content }, index) =>
        content ? (
          <Descriptions.Item key={index} label={t(label)}>
            {content}
          </Descriptions.Item>
        ) : null,
      )}
    </Descriptions>
  )

  return selected && result ? renderDescriptions(paramsList) : null
}

function getFusionParams(params: YModels.FusionParams) {
  return [
    { label: 'task.fusion.form.dataset', content: <VersionName id={params.dataset_id} /> },
    { label: 'task.fusion.form.sampling', content: params.sampling_count },
    {
      label: 'task.fusion.form.includes.label',
      content: params.include_datasets?.length ? params.include_datasets?.map((ds) => <Tag key={ds}><VersionName id={ds} /></Tag>) : null,
    },
    {
      label: 'task.train.form.repeatdata.label',
      content: params.merge_strategy ? t(getMergeStrategyLabel(params.merge_strategy)) : null,
    },
    {
      label: 'task.fusion.form.excludes.label',
      content: params.exclude_datasets?.map((ds) => <Tag key={ds}><VersionName id={ds} /></Tag>),
    },
    {
      label: 'task.fusion.form.class.include.label',
      content: params.include_labels?.join(','),
    },
    {
      label: 'task.fusion.form.class.exclude.label',
      content: params.exclude_labels?.join(','),
    },
  ]
}

function getMiningParams(params: YModels.MiningParams) {
  return [
    { label: 'task.mining.form.image.label', content: <ImageName id={params.docker_image_id} /> },
    { label: 'task.mining.form.dataset.label', content: <VersionName id={params.dataset_id} /> },
    { label: 'task.mining.form.model.label', content: <ModelVersionName id={params.model_id} /> },
    { label: 'task.mining.form.topk.label', content: params.top_k },
    {
      label: 'task.mining.form.label.label',
      content: params.labels?.join(','),
    },
    { label: 'task.gpu.count', content: 0 },
    imageConfig(params.config),
  ]
}

function getLabelParams(params: YModels.LabelParams) {
  return [
    { label: 'task.fusion.form.dataset', content: <VersionName id={params.dataset_id} /> },
    { label: 'task.label.form.keep_anno.label', content: t(getLabelAnnotationType(params.annotation_type)) },
    { label: 'task.label.form.desc.label', content: params.extra_url ? <a href={params.extra_url}>{params.extra_url}</a> : null },
  ]
}

function getMergeParams(params: YModels.MergeParams) {
  return [
    { label: 'task.fusion.form.dataset', content: <VersionName id={params.dataset_id} /> },
    {
      label: 'task.fusion.form.merge.include.label',
      content: params.include_datasets?.length ? params.include_datasets?.map((ds) => <Tag key={ds}><VersionName id={ds} /></Tag>) : null,
    },
    {
      label: 'task.fusion.form.merge.exclude.label',
      content: params.exclude_datasets?.length ? params.exclude_datasets?.map((ds) => <Tag key={ds}><VersionName id={ds} /></Tag>) : null,
    },
  ]
}

function getTrainingParams(params: YModels.TrainingParams) {
  return [
    { label: 'task.train.form.image.label', content: <ImageName id={params.docker_image_id} /> },
    { label: 'task.train.form.trainsets.label', content: <VersionName id={params.dataset_id} /> },
    { label: 'task.train.form.testsets.label', content: <VersionName id={params.validation_dataset_id} /> },
    { label: 'task.detail.label.premodel', content: params.model_id ? <ModelVersionName id={params.model_id} stageId={params.model_stage_id} /> : null },
    { label: 'task.gpu.count', content: params.gpuCount },
    imageConfig(params.config),
  ]
}

function imageConfig(config: { [key: string]: string | number } = {}) {
  return {
    label: 'task.train.form.hyperparam.label',
    content: Object.keys(config).map((key) => (
      <Row key={key} align="middle" style={{ flexWrap: 'wrap', flex: '0 0 100%', width: '100%' }}>
        <Col flex={'200px'} style={{ fontWeight: 'bold' }}>
          {key}:
        </Col>
        <Col flex={1}>{config[key].toString()}</Col>
      </Row>
    )),
  }
}

export default FinishStep
