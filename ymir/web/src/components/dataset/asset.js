import React, { useEffect, useRef, useState } from "react"
import { Button, Card, Col, Descriptions, Image, List, Row, Tag } from "antd"
import { connect } from "dva"
import styles from "./common.less"
import { getDateFromTimestamp } from "@/utils/date"
import Hash from "../common/hash"
import AssetAnnotation from "./asset_annotation"
import { useHistory, useParams } from "react-router"

import t from "@/utils/t"

const { CheckableTag } = Tag

const KeywordColor = [
  "green",
  "red",
  "blue",
  "purple",
  "volcano",
  "lime",
  "geekblue",
  "orange",
  "gold",
  "cyan",
]

function Assets({ getAsset }) {
  const history = useHistory()
  const { id, hash } = useParams()
  console.log("params: ", id, hash)
  const [asset, setAsset] = useState({})
  const imgContainer = useRef()
  const [imgWidth, setImgWidth] = useState(600)
  const [selectedKeywords, setSelectedKeywords] = useState([])

  useEffect(async () => {
    const result = await getAsset(id, hash)
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
    console.log('keywords: ', keywords, annotations)
    setAsset({ ...result, keywords })
  }, [id, hash])

  function calImgWidth() {
    const img = imgContainer.current.firstChild
    const cw = imgContainer.current.clientWidth
    const iw = img.width
    let result = cw - 20
    setImgWidth(result)
  }

  function changeKeywords(tag, checked) {
    const selected = checked
      ? [...selectedKeywords, tag]
      : selectedKeywords.filter((k) => k !== tag)
    setSelectedKeywords(selected)
  }

  async function randomAsset() {
    const result = await getAsset(id, "random")
    history.push(`/home/dataset/asset/${id}/${result.hash}`)
  }

  return hash ? (
    <div>
      <Row>
        <Col flex="auto" className={styles.asset_img} ref={imgContainer}>
          <img
            src={asset.url}
            style={{width: imgWidth}}
            className={styles.assetImg}
            onLoad={() => calImgWidth()}
          />
          {asset.annotations ? (
            <AssetAnnotation
              ratio={imgWidth / (asset.metadata?.width || imgWidth)}
              width={imgWidth}
              assetId={asset.id}
              filters={selectedKeywords}
              colors={KeywordColor}
              data={asset?.annotations}
            />
          ) : null}
        </Col>
        <Col flex="300px" className={styles.asset_info}>
          <Card
            title={t("dataset.asset.info")}
            bordered={false}
            style={{ width: "100%" }}
            bodyStyle={{ padding: "24px 0" }}
          >
            <Descriptions
              column={1}
              bordered
              contentStyle={{ padding: "0 10px" }}
              labelStyle={{ padding: "10px" }}
            >
              <Descriptions.Item label={t("dataset.asset.info.id")}>
                <Hash value={hash} />
              </Descriptions.Item>
              {asset.size ? (
                <Descriptions.Item label={t("dataset.asset.info.size")}>
                  {asset.size}
                </Descriptions.Item>
              ) : null}
              <Descriptions.Item label={t("dataset.asset.info.width")}>
                {asset.metadata?.width}
              </Descriptions.Item>
              <Descriptions.Item label={t("dataset.asset.info.height")}>
                {asset.metadata?.height}
              </Descriptions.Item>
              <Descriptions.Item label={t("dataset.asset.info.channel")}>
                {asset.metadata?.channel}
              </Descriptions.Item>
              <Descriptions.Item label={t("dataset.asset.info.timestamp")}>
                {getDateFromTimestamp(asset.metadata?.timestamp)}
              </Descriptions.Item>
              <Descriptions.Item label={t("dataset.asset.info.keyword")}>
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

export default connect(null, actions)(Assets)
