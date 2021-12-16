
import { useHistory, useParams } from "react-router"
import React, { useEffect, useRef, useState } from "react"
import { Button, Card, Col, Descriptions, Row, Tag } from "antd"
import { connect } from "dva"

import { getDateFromTimestamp } from "@/utils/date"
import t from "@/utils/t"
import Hash from "@/components/common/hash"
import AssetAnnotation from "@/components/dataset/asset_annotation"
import styles from "./asset.less"
import { NavDatasetIcon } from '@/components/common/icons'
import { EyeOffIcon, EyeOnIcon } from "@/components/common/icons"

const { CheckableTag } = Tag

const KeywordColor = [
  "green",
  "red",
  "cyan",
  "blue",
  "yellow",
  "purple",
  "magenta",
  "orange",
  "gold",
]

function Asset({ id, hash, getAsset }) {
  const history = useHistory()
  const [asset, setAsset] = useState({})
  const [current,  setCurrent] = useState('')
  const [showAnnotations, setShowAnnotations] = useState([])
  const [selectedKeywords, setSelectedKeywords] = useState([])

  useEffect(() => {
    hash && setCurrent(hash)
  }, [hash])

  useEffect(async () => {
    const result = await getAsset(id, current)
    const compare = (a, b) => {
      const aa = (a.keyword || a).toUpperCase()
      const bb = (b.keyword || b).toUpperCase()
      if (aa > bb) {
        return -1
      }
      if (aa < bb) {
        return 1
      }
      return 0
    }
    const keywords = result.keywords.sort(compare)
    const annotations = result.annotations.sort(compare)
    setAsset({ ...result, keywords, annotations })
    setSelectedKeywords(keywords)
  }, [id, current])

  useEffect(() => {
    setShowAnnotations((asset.annotations || []).filter(anno => selectedKeywords.indexOf(anno.keyword) >= 0))
  }, [selectedKeywords])

  function changeKeywords(tag, checked) {
    const selected = checked
      ? [...selectedKeywords, tag]
      : selectedKeywords.filter((k) => k !== tag)
    setSelectedKeywords(selected)
  }

  function toggleAnnotation() {
    setSelectedKeywords(selectedKeywords.length ? [] : asset.keywords)
  }

  async function randomAsset() {
    const result = await getAsset(id, "random")
    if (result) {
      setCurrent(result.hash)
    }
  }

  return asset.hash ? (
    <div className={styles.asset}>
      <div className={styles.info}>
        <Row className={styles.infoRow} wrap={false}>
          <Col span={18} className={styles.asset_img}>
            {asset.annotations ? (
              <AssetAnnotation
                url={asset.url}
                keywords={asset.keywords}
                data={showAnnotations}
              // toggleHandle={toggleAnnotation}
              />
            ) : null}
          </Col>
          <Col span={6} className={styles.asset_info}>
            <Card
              title={<><NavDatasetIcon /> {t("dataset.asset.info")}</>}
              bordered={false}
              style={{ marginRight: 20 }}
              headStyle={{ paddingLeft: 0 }}
              bodyStyle={{ padding: "20px 0" }}
            >
              <Descriptions
                bordered
                column={2}
                contentStyle={{ flexWrap: 'wrap', padding: '10px' }}
                labelStyle={{ justifyContent: 'flex-end', padding: '10px' }}
              >
                <Descriptions.Item label={t("dataset.asset.info.id")} span={2}>
                  <Hash value={current} />
                </Descriptions.Item>
                <Descriptions.Item label={t("dataset.asset.info.width")}>
                  {asset.metadata?.width}
                </Descriptions.Item>
                <Descriptions.Item label={t("dataset.asset.info.height")}>
                  {asset.metadata?.height}
                </Descriptions.Item>
                {asset.size ? (
                  <Descriptions.Item label={t("dataset.asset.info.size")}>
                    {asset.size}
                  </Descriptions.Item>
                ) : null}
                <Descriptions.Item label={t("dataset.asset.info.channel")} span={asset.size ? 1 : 2}>
                  {asset.metadata?.channel}
                </Descriptions.Item>
                <Descriptions.Item label={t("dataset.asset.info.timestamp")} span={2}>
                  {getDateFromTimestamp(asset.metadata?.timestamp)}
                </Descriptions.Item>
                <Descriptions.Item label={t("dataset.asset.info.keyword")} span={2}>
                  <Row>
                    <Col flex={1}>
                    {asset.keywords?.map((keyword, i) => (
                      <CheckableTag
                        checked={selectedKeywords.indexOf(keyword) > -1}
                        onChange={(checked) => changeKeywords(keyword, checked)}
                        className={'ant-tag-' + KeywordColor[i % (KeywordColor.length + 1)]}
                        key={i}
                      >
                        {keyword}
                      </CheckableTag>
                    ))}
                    </Col>
                    <Col>
                      {selectedKeywords.length ? 
                        <EyeOnIcon onClick={toggleAnnotation} title={t("dataset.asset.annotation.hide")} /> : 
                        <EyeOffIcon onClick={toggleAnnotation} title={t("dataset.asset.annotation.show")} />}
                    </Col>
                  </Row>
                </Descriptions.Item>
              </Descriptions>
              <Button
                type="primary"
                style={{ marginTop: 20 }}
                onClick={randomAsset}
              >
                {t("dataset.asset.random")}
              </Button>
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  ) : (
    <div>{t("dataset.asset.empty")}</div>
  )
}

const actions = (dispatch) => {
  return {
    getAsset(id, hash) {
      return dispatch({
        type: "dataset/getAsset",
        payload: { id, hash },
      })
    },
  }
}

export default connect(null, actions)(Asset)
