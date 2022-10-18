import React, { useEffect } from "react"
import { useHistory } from "umi"
import { Button, Col, Descriptions, Row, Tag } from "antd"

import t from "@/utils/t"
import { ResultStates } from '@/constants/common'
import styles from "./detail.less"
import { SearchIcon } from "@/components/common/icons"
import { DescPop } from "../common/descPop"

const { Item } = Descriptions
const labelStyle = { width: '15%', paddingRight: '20px', justifyContent: 'flex-end' }

function DatasetDetail({ dataset = {} }) {
  const history = useHistory()
  const { cks = {}, tags = {}, inferClass } = dataset

  const renderKeywords = (anno, label = t('annotation.gt')) => {
    if (!anno) {
      return
    }
    const { keywords = [], count = {} } = anno
    return <p>
      {label}: {keywords.map(keyword => <Tag key={keyword}>{keyword}({count[keyword]})</Tag>)}
    </p>
  }

  const renderCk = (label = 'ck', keywords = []) => keywords.length ? <Item label={label}>
    {keywords.map(({ keyword, children }) => <Row key={keyword}>
      <Col flex={'160px'}>{keyword}</Col>
      <Col>{children.map(({ keyword, count }) => <Tag key={keyword}>{keyword}({count})</Tag>)}</Col>
    </Row>)}
  </Item> : null
  return (
    <div className='datasetDetail'>
      <Descriptions
        bordered
        column={2}
        labelStyle={labelStyle}
        className='infoTable'
      >
        <Item label={t("dataset.detail.label.name")} span={2}>
          <Row>
            <Col flex={1}>{dataset.name} {dataset.versionName}</Col>
            <Col hidden={dataset.state !== ResultStates.VALID}>
              <Button
                type='primary'
                icon={<SearchIcon />}
                onClick={() => history.push(`/home/project/${dataset.projectId}/dataset/${dataset.id}/assets`)}
              >{t('common.view')}</Button>
            </Col>
          </Row>
        </Item>
        <Item label={t("dataset.detail.label.keywords")}>
          {renderKeywords(dataset.gt)}
          {renderKeywords(dataset.pred, t('annotation.pred'))}
          {inferClass ? <div>{t('dataset.detail.infer.class')}{inferClass.map(cls => <Tag key={cls}>{cls}</Tag>)}</div> : null}
        </Item>
        <Item label={t("dataset.detail.label.assets")} contentStyle={{ minWidth: 150 }}>{dataset.assetCount}</Item>
        {dataset.hidden ? <Item label={t("common.hidden.label")}>{t('common.state.hidden')}</Item> : null}
        {renderCk(t('dataset.assets.keyword.selector.types.cks'), cks.keywords)}
        {renderCk(t('dataset.assets.keyword.selector.types.tags'), tags.keywords)}
        <Item label={t("common.desc")}><DescPop description={dataset.description} /></Item>
      </Descriptions>
    </div>
  )
}

export default DatasetDetail
