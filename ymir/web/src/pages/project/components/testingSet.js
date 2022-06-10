import { Col, Popover, Row, Tag } from "antd"
import KeywordRates from "@/components/dataset/keywordRates"
import t from "@/utils/t"
import s from "../detail.less"

export const TestingSet = ({ project }) => {

  function renderProjectTestingSetLabel() {
    const getDsName = (ds = {}) => ds.name ? (ds.name + ' ' + (ds.versionName || '')) : ''
    const getAssetCount = (ds = {}) => ds.assetCount ? ds.assetCount : ''
    const getDatasetGroup = (dsg = []) => {
      return dsg.map(ds => {
        return {
          name: getDsName(ds),
          assetCount: getAssetCount(ds),
          dataset: ds
        }
      })
    }
    const maps = [
      { label: 'project.add.form.testing.set', datasetGroup: getDatasetGroup(project.testingSetGroup) }
    ]

    return maps.map(({ label, datasetGroup }) => {
      return <Row key={label} className={s.datasetPanel} align='left'>
        <Col className={s.datasetTitle}>
          <span>{t(label)}: </span>
        </Col>
        <Col flex={1}>
          {datasetGroup.map(({name, dataset, assetCount}) => {
            const rlabel = name ? <Tag className={s.nameTag}>{name}{assetCount ? `(${assetCount})` : ''}</Tag> : ''
            return <span key={name} title={name}>{dataset ? renderPop(rlabel, dataset) : rlabel}</span>})}
        </Col>
      </Row>
      
    })
  }

  function renderPop(label, dataset = {}) {
    dataset.project = project
    const content = <KeywordRates dataset={dataset} progressWidth={0.4}></KeywordRates>
    return <Popover content={content} overlayInnerStyle={{ minWidth: 500 }}>
      <span>{label}</span>
    </Popover>
  }

  return (<>
      {renderProjectTestingSetLabel()}
    </>
  )
}
