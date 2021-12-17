import React, { useState, useEffect } from "react"
import { connect } from 'dva'
import { Row, Col, Button, Image, Slider, Space, Empty, Form, Card, Descriptions, Tag, InputNumber } from "antd"
import { useParams, useHistory } from "umi"

import t from "@/utils/t"
import { format } from '@/utils/date'
import Breadcrumb from '@/components/common/breadcrumb'
import Uploader from "../../components/form/uploader"
import AssetAnnotation from "@/components/dataset/asset_annotation"
import styles from './verify.less'
import { NavDatasetIcon, EqualizerIcon } from '@/components/common/icons'
import ImgDef from '@/assets/img_def.png'

const { CheckableTag } = Tag


const KeywordColor = ["green", "red", "cyan", "blue", "yellow", "purple", "magenta", "orange", "gold"]


function Verify({ getModel, verify }) {
  const history = useHistory()
  const { id } = useParams()
  const [model, setModel] = useState({})
  const [url, setUrl] = useState('')
  const [confidence, setConfidence] = useState(20)
  const [annotations, setAnnotations] = useState([])
  const [showAnnotations, setShowAnnos] = useState([])
  const [selectedKeywords, setSelectedKeywords] = useState([])
  const IMGSIZELIMIT = 10

  useEffect(async () => {
    const result = await getModel(id)
    if (result) {
      setModel(result)
    }
  }, [])

  useEffect(async () => {
    if (url) {
      // reinit annotations
      setAnnotations([])
      const result = await verify(id, [url])
      // console.log('result: ', result)
      if (result) {
        const all = result.annotations[0]?.detection || []

        setAnnotations(all)
        if (all.length) {
          setSelectedKeywords([...new Set(all.map(anno => anno.keyword))])
        }
      }
    }
  }, [url])

  useEffect(() => {
    setShowAnnos(annotations.length ? annotations.filter(anno => 
      anno.score * 100 > confidence && selectedKeywords.indexOf(anno.keyword) > -1
    ) : [])
  }, [confidence, annotations, selectedKeywords])

  const renderTitle = (
    <Row>
      <Col flex={1}>{model.name}</Col>
      <Col><Button type='link' onClick={() => history.goBack()}>{t('common.back')}&gt;</Button></Col>
    </Row>
  )

  const renderUploader = (
    <div className={styles.uploader}>
      <div className={styles.emptyImg}>
        <img src={ImgDef} />
        <p>{t('model.verify.upload.tip')}</p>
        <p>{t('model.verify.upload.info', { size: IMGSIZELIMIT })}</p>
        {renderUploadBtn()}
      </div>
    </div>
  )

  // annotations.filter(anno => anno.confidence > confidence)
  function renderUploadBtn(label = t('model.verify.upload.label')) {
    return (
      <Uploader
        key={'uploader'}
        type='primary'
        className={styles.verify_uploader}
        onChange={(files, result) => { setUrl(files.length ? result : '') }}
        format='img'
        label={label}
        showUploadList={false}
        max={IMGSIZELIMIT}
      />
    )
  }

  function getExtrameScore(max = 'max') {
    const scores = annotations.map(anno => anno.score)
    return scores ? `${(Math[max](...scores) * 100).toFixed(2)}%` : ''
  }


  function changeKeywords(tag, checked) {
    const selected = checked
      ? [...selectedKeywords, tag]
      : selectedKeywords.filter((k) => k !== tag)
    setSelectedKeywords(selected)
  }

  function toggleAnnotation() {
    setSelectedKeywords(selectedKeywords.length ? [] : model.keywords)
  }

  function confidenceChange(value) {
    const cfc = Number(value) || 0
    // console.log('number: ', cfc, value)
    setConfidence(cfc)
  }

  return (
    <div className={styles.modelVerify}>
      <Breadcrumb />
      <Card className={styles.info} bodyStyle={{ padding: 20, height: '100%' }} title={renderTitle}>
        <Row className={styles.infoRow} wrap={false}>
          <Col span={18} className={styles.asset_img}>
            {url ? (
              <AssetAnnotation
                url={url}
                keywords={model.keywords}
                data={showAnnotations}
              />
            ) : renderUploader}
          </Col>
          <Col span={6} className={styles.asset_info}>
            <Card
              title={<><EqualizerIcon /> {t("model.verify.confidence.title")}</>}
              bordered={false}
              style={{ marginRight: 20 }}
              headStyle={{ paddingLeft: 0 }}
              bodyStyle={{ padding: "20px 0 0" }}
            >
              <Form><Form.Item label={t('model.verify.confidence')}>
                <Row gutter={10}>
                  <Col flex={1}>
                <Slider marks={{ 0: '0%', 100: '100%' }}
                  tipFormatter={(value) => `${value}%`} value={confidence} onChange={confidenceChange} />
                  </Col>
                  <Col><InputNumber value={confidence} style={{ width: 60 }} precision={0} min={0} max={100} onChange={confidenceChange} /></Col>
                </Row>
              </Form.Item></Form>
            </Card>
            <Card
              title={<><NavDatasetIcon /> {t("model.verify.model.info.title")}</>}
              bordered={false}
              style={{ marginRight: 20 }}
              headStyle={{ paddingLeft: 0 }}
              bodyStyle={{ padding: "20px 0" }}
            >
              <Descriptions
                bordered
                column={1}
                contentStyle={{ flexWrap: 'wrap', padding: '10px' }}
                labelStyle={{ justifyContent: 'flex-end', padding: '10px' }}
              >
                <Descriptions.Item label={t("model.column.name")}>
                  {model.name}
                </Descriptions.Item>
                <Descriptions.Item label={'mAP'}>
                  {model.map}
                </Descriptions.Item>
                <Descriptions.Item label={t("model.column.create_time")}>
                  {format(model.create_datetime)}
                </Descriptions.Item>
                <Descriptions.Item label={t("dataset.asset.info.keyword")}>
                  {model.keywords?.map((keyword, i) => (
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
              <div style={{ marginTop: 20 }}>{url ? renderUploadBtn(t('model.verify.reverify.label')) : null}</div>
            </Card>
          </Col>
        </Row>
      </Card>
    </div>
  )
}

const actions = (dispatch) => ({
  getModel(payload) {
    return dispatch({
      type: 'model/getModel',
      payload,
    })
  },
  verify(id, urls) {
    return dispatch({
      type: 'model/verify',
      payload: { id, urls },
    })
  },
})

export default connect(null, actions)(Verify)
