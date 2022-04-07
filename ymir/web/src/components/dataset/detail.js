import React from "react"
import { useHistory } from "umi"
import { Button, Col, Descriptions, Row, Tag } from "antd"

import t from "@/utils/t"
import styles from "./detail.less"
import { SearchIcon } from "@/components/common/icons"

const { Item } = Descriptions

function DatasetDetail({ dataset = {} }) {
  const history = useHistory()

  const labelStyle = { width: '15%', paddingRight: '20px', justifyContent: 'flex-end' }

  return (
    <div className={styles.datasetDetail}>
      <Descriptions
        bordered
        column={1}
        labelStyle={labelStyle}
        className={styles.infoTable}
      >
        <Item label={t("dataset.detail.label.name")}>
          <Row><Col flex={1}>{dataset.name}</Col>
            <Col><Button type='primary' icon={<SearchIcon />} onClick={() => history.push(`/home/project/${pid}/dataset/${dataset.id}/assets`)}>{t('common.view')}</Button></Col></Row></Item>
        <Item label={t("dataset.detail.label.assets")}>{dataset.assetCount}</Item>
        <Item label={t("dataset.detail.label.keywords")}>{dataset?.keywords?.map(keyword => <Tag key={keyword}>{keyword}</Tag>)}</Item>
      </Descriptions>
    </div>
  )
}

export default DatasetDetail
