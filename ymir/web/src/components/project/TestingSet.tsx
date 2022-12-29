import React, { FC, ReactElement, useEffect } from 'react'
import useFetch from '@/hooks/useFetch'
import { Col, Popover, Row, Tag } from 'antd'
import SampleRates from '@/components/dataset/SampleRates'
import t from '@/utils/t'
import s from './testingset.less'
type Props = {
  project: YModels.Project
}
const TestingSet: FC<Props> = ({ project }) => {
  const [datasets, fetchDatasets] = useFetch('dataset/batchDatasets', [])

  useEffect(() => {
    project?.testingSets?.length && fetchDatasets({ pid: project.id, ids: project.testingSets })
  }, [project.testingSets])

  function renderProjectTestingSetLabel() {
    const getDsName = (ds: YModels.Dataset) => (ds.name ? ds.name + ' ' + (ds.versionName || '') : '')
    const getAssetCount = (ds: YModels.Dataset) => (ds.assetCount ? ds.assetCount : '')
    const getDatasetGroup = (dsg = []) => {
      return dsg.map((ds) => {
        return {
          name: getDsName(ds),
          assetCount: getAssetCount(ds),
          dataset: ds,
        }
      })
    }
    const maps = [{ label: 'project.add.form.testing.set', datasetGroup: getDatasetGroup(datasets) }]

    return maps.map(({ label, datasetGroup }) => {
      return (
        <Row key={label} className={s.testingSets}>
          <Col className={s.datasetTitle}>
            <span>{t(label)}: </span>
          </Col>
          <Col flex={1}>
            {datasetGroup.map(({ name, dataset, assetCount }) => {
              const rlabel = name ? (
                <Tag className={s.nameTag}>
                  {name}
                  {assetCount ? `(${assetCount})` : ''}
                </Tag>
              ) : (
                ''
              )

              return (
                <span key={name} title={name}>
                  {dataset ? renderPop(rlabel, dataset) : rlabel}
                </span>
              )
            })}
          </Col>
        </Row>
      )
    })
  }

  function renderPop(label: string | ReactElement, dataset: YModels.Dataset) {
    dataset.project = project
    const content = <SampleRates keywords={project?.keywords} dataset={dataset} progressWidth={0.4} />
    return (
      <Popover content={content} overlayInnerStyle={{ minWidth: 500 }}>
        <span>{label}</span>
      </Popover>
    )
  }

  return datasets.length ? <>{renderProjectTestingSetLabel()}</> : null
}

export default TestingSet
