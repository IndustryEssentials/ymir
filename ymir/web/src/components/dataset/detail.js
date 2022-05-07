import React from "react"
import { useHistory } from "umi"
import { Button, Col, Descriptions, Row, Tag } from "antd"

import t from "@/utils/t"
import { states } from '@/constants/common'
import styles from "./detail.less"
import { SearchIcon } from "@/components/common/icons"

const { Item } = Descriptions

function DatasetDetail({ dataset = {} }) {
  const history = useHistory()

  const labelStyle = { width: '15%', paddingRight: '20px', justifyContent: 'flex-end' }

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
            <Col hidden={dataset.state !== states.VALID}>
              <Button
                type='primary'
                icon={<SearchIcon />}
                onClick={() => history.push(`/home/project/${dataset.projectId}/dataset/${dataset.id}/assets`)}
              >{t('common.view')}</Button>
            </Col>
          </Row>
        </Item>
        <Item label={t("dataset.detail.label.assets")}>{dataset.assetCount}</Item>
        {dataset.hidden ? <Item label={t("common.hidden.label")}>{t('common.state.hidden')}</Item> : null }
        <Item label={t("dataset.detail.label.keywords")}>{dataset?.keywords?.map(keyword => <Tag key={keyword}>{keyword}</Tag>)}</Item>
      </Descriptions>
    </div>
  )
}

export default DatasetDetail
