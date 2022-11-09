import { Descriptions } from 'antd'
import React, { useEffect, useState } from 'react'
import { Link, useSelector } from 'umi'

import t from '@/utils/t'
import { STEP } from '@/constants/iteration'
import VersionName from '@/components/result/VersionName'
import ModelVersionName from '@/components/result/ModelVersionName'

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
    console.log('result:', result)
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
    setParamsList(maps[step.value]({ ...task.parameters, gpuCount: task?.config?.gpu_count }))
  }, [result])

  const renderDescriptions = (list: ListType) => (
    <Descriptions column={2}>
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
      content: params.include_datasets?.length ? params.include_datasets?.map((ds) => <VersionName key={ds} id={ds} />) : null,
    },
    {
      label: 'task.train.form.repeatdata.label',
      content: params.merge_strategy,
    },
    {
      label: 'task.fusion.form.excludes.label',
      content: params.exclude_datasets?.map((ds) => <VersionName key={ds} id={ds} />),
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
    { label: 'task.mining.form.image.label', content: params.docker_image_id },
    { label: 'task.mining.form.dataset.label', content: <VersionName id={params.dataset_id} /> },
    { label: 'task.mining.form.model.label', content: <ModelVersionName id={params.model_id} /> },
    { label: 'task.mining.form.topk.label', content: params.top_k },
    {
      label: 'task.mining.form.label.label',
      content: params.labels?.join(','),
    },
    { label: 'task.gpu.count', content: 0 },
  ]
}

function getLabelParams(params: YModels.LabelParams) {
  return [
    { label: 'task.fusion.form.dataset', content: <VersionName id={params.dataset_id} /> },
    { label: 'task.label.form.desc.label', content: params.extra_url ? <a href={params.extra_url}>{params.extra_url}</a> : null },
  ]
}

function getMergeParams(params: YModels.MergeParams) {
  return [
    { label: 'task.fusion.form.dataset', content: <VersionName id={params.dataset_id} /> },
    {
      label: 'task.fusion.form.merge.include.label',
      content: params.include_datasets?.length ? params.include_datasets?.map((ds) => <VersionName key={ds} id={ds} />) : null,
    },
    {
      label: 'task.fusion.form.merge.exclude.label',
      content: params.exclude_datasets?.map((ds) => <VersionName key={ds} id={ds} />),
    },
  ]
}

function getTrainingParams(params: YModels.TrainingParams) {
  return [
    { label: 'task.train.form.image.label', content: params.dataset_id },
    { label: 'task.train.form.trainsets.label', content: <VersionName id={params.dataset_id} /> },
    { label: 'task.train.form.testsets.label', content: <VersionName id={params.validation_dataset_id} /> },
    { label: 'task.detail.label.premodel', content: <ModelVersionName id={params.model_id} stageId={params.model_stage_id} /> },
    { label: 'task.gpu.count', content: params.gpuCount },
    { label: 'task.train.export.format', content: params.dataset_id },
  ]
}

export default FinishStep
