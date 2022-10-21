import React, { useState, useEffect } from "react"
import { connect } from 'dva'
import { Row, Col, Input, Button, Image, Slider, Space, Empty, Form, Card, Descriptions, Tag, InputNumber } from "antd"
import {
  UpOutlined,
  DownOutlined,
} from '@ant-design/icons'
import { useParams, useHistory } from "umi"

import t from "@/utils/t"
import { format } from '@/utils/date'
import Breadcrumb from '@/components/common/breadcrumb'
import Uploader from "@/components/form/uploader"
import AssetAnnotation from "@/components/dataset/assetAnnotation"
import { TYPES } from '@/constants/image'
import styles from './verify.less'
import { NavDatasetIcon, SearchEyeIcon, NoXlmxIcon } from '@/components/common/icons'
import ImgDef from '@/assets/img_def.png'
import ImageSelect from "@/components/form/imageSelect"
import { percent } from "@/utils/number"
import useFetch from '@/hooks/useFetch'

const { CheckableTag } = Tag


const KeywordColor = ["green", "red", "cyan", "blue", "yellow", "purple", "magenta", "orange", "gold"]


function Verify({ verify }) {
  const history = useHistory()
  const { mid: id, id: pid } = useParams()
  const [url, setUrl] = useState('')
  const [confidence, setConfidence] = useState(20)
  const [annotations, setAnnotations] = useState([])
  const [showAnnotations, setShowAnnos] = useState([])
  const [selectedKeywords, setSelectedKeywords] = useState([])
  const [form] = Form.useForm()
  const [image, setImage] = useState(null)
  const [seniorConfig, setSeniorConfig] = useState([])
  const [hpVisible, setHpVisible] = useState(false)
  const IMGSIZELIMIT = 10
  const [model, getModel] = useFetch('model/getModel', {})

  useEffect(() => {
    getModel({ id })
  }, [])

  useEffect(() => {
    setShowAnnos(annotations.length ? annotations.filter(anno =>
      anno.score * 100 > confidence && selectedKeywords.indexOf(anno.keyword) > -1
    ) : [])
  }, [confidence, annotations, selectedKeywords])

  useEffect(() => {
    form.setFieldsValue({ hyperparam: seniorConfig })
  }, [seniorConfig])

  function imageChange(value, option) {
    if (option) {
      setImage(option.url)
    }
    const { configs } = option || {}
    const configObj = (configs || []).find(conf => conf.type === TYPES.INFERENCE) || {}
    setConfig(configObj.config)
  }

  function urlChange(files, url) {
    setUrl('')
    setUrl(files.length ? url : '')
    setAnnotations([])
  }

  function setConfig(config = {}) {
    const params = Object.keys(config).filter(key => key !== 'gpu_count').map(key => ({ key, value: config[key] }))
    setSeniorConfig(params)
  }

  const renderTitle = (
    <Row>
      <Col>{model.name}</Col>
      <Col flex={1}>
      </Col>
      <Col><Button type='link' onClick={() => history.goBack()}>{t('common.back')}&gt;</Button></Col>
    </Row>
  )

  const renderUploader = (
    <div className={styles.uploader}>
      <div className={styles.emptyImg}>
        <img src={ImgDef} />
        <p>{t('model.verify.upload.tip')}</p>
        <p>{t('model.verify.upload.info', { size: IMGSIZELIMIT })}</p>
      </div>
    </div>
  )

  function renderUploadBtn(label = t('model.verify.upload.label')) {
    return (
      <Uploader
        key={'uploader'}
        type='primary'
        className={styles.verify_uploader}
        onChange={urlChange}
        format='img'
        label={label}
        showUploadList={false}
        max={IMGSIZELIMIT}
      />
    )
  }

  function changeKeywords(tag, checked) {
    const selected = checked
      ? [...selectedKeywords, tag]
      : selectedKeywords.filter((k) => k !== tag)
    setSelectedKeywords(selected)
  }

  function confidenceChange(value) {
    const cfc = Number(value) || 0
    setConfidence(cfc)
  }

  async function verifyImg() {
    const config = {}
    form.getFieldValue('hyperparam').forEach(({ key, value }) => key && value ? config[key] = value : null)
    // reinit annotations
    setAnnotations([])
    const result = await verify({ projectId: pid, modelStage: [id, model.recommendStage], urls: [url], image, config })
    if (result) {
      const all = result || []

      setAnnotations(all)
      if (all.length) {
        setSelectedKeywords([...new Set(all.map(anno => anno.keyword))])
      }
    }
  }

  async function validHyperparam(rule, value) {

    const params = form.getFieldValue('hyperparam').map(({ key }) => key)
      .filter(item => item && item.trim() && item === value)
    if (params.length > 1) {
      return Promise.reject(t('task.validator.same.param'))
    } else {
      return Promise.resolve()
    }
  }

  const onFinish = () => {
    form.validateFields().then(() => {
      verifyImg()
    })
  }

  return (
    <div className={styles.modelVerify}>
      <Breadcrumb />
      <Card className={styles.info} bodyStyle={{ padding: 20, height: '100%' }} title={renderTitle}>
        <Row className={styles.infoRow} wrap={false}>
          <Col span={18} className={`${styles.asset_img} scrollbar`}>
            {url ? (
              <AssetAnnotation
                url={url}
                keywords={model.keywords}
                data={showAnnotations}
              />
            ) : renderUploader}
            {url ? (<Form className={styles.confidence}><Form.Item label={t('model.verify.confidence')}>
              <Row gutter={10}>
                <Col flex={1}>
                  <Slider marks={{ 0: '0%', 100: '100%' }} style={{ width: 200 }}
                    tipFormatter={(value) => `${value}%`} value={confidence} onChange={confidenceChange} />
                </Col>
                <Col><InputNumber value={confidence} style={{ width: 60, borderColor: 'rgba(0, 0, 0, 0.15)', margin: 5, height: 35 }} precision={0} min={0} max={100} onChange={confidenceChange} /></Col>
              </Row>
            </Form.Item></Form>
            ) : null}
          </Col>
          <Col span={6} className={`${styles.asset_info} scrollbar`}>
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
                  <span title={model.map}>{percent(model.map)}</span>
                </Descriptions.Item>
                <Descriptions.Item label={t("model.column.create_time")}>
                  {model.createTime}
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
            </Card>

            <Form form={form} className={styles.asset_form}>
              <Form.Item name='image' label={t('task.inference.form.image.label')} rules={[{ required: true }]}>
                <ImageSelect style={{ width: 200 }} type={TYPES.INFERENCE} placeholder={t('task.train.form.image.placeholder')} onChange={imageChange} />
              </Form.Item>

              {seniorConfig.length ?
                <Card
                  title={<><SearchEyeIcon /> {t("model.verify.model.param.title")}</>}
                  bordered={false}
                  style={{ marginRight: 20 }}
                  headStyle={{ padding: 0, minHeight: 28 }}
                  bodyStyle={{ padding: 0 }}
                  extra={<Button type='link'
                    onClick={() => setHpVisible(!hpVisible)}
                    style={{ paddingLeft: 0 }}
                  >{hpVisible ? t('model.verify.model.param.fold') : t('model.verify.model.param.unfold')}{hpVisible ? <UpOutlined /> : <DownOutlined />}
                  </Button>}
                >
                  <Form.Item
                    rules={[{ validator: validHyperparam }]}
                  >
                    <Form.List name='hyperparam'>
                      {(fields, { add, remove }) => (
                        <>
                          <div className={styles.paramContainer} hidden={!hpVisible}>
                            <Row style={{ backgroundColor: '#fafafa', border: '1px solid #f4f4f4', lineHeight: '40px', marginBottom: 10 }} gutter={10}>
                              <Col flex={'150px'}>{t('common.key')}</Col>
                              <Col flex={1}>{t('common.value')}</Col>
                            </Row>
                            <div className={styles.paramField} >
                              {fields.map(field => (
                                <Row key={field.key} gutter={10}>
                                  <Col flex={'150px'}>
                                    <Form.Item
                                      {...field}
                                      name={[field.name, 'key']}
                                      fieldKey={[field.fieldKey, 'key']}
                                      rules={[
                                        { validator: validHyperparam }
                                      ]}
                                    >
                                      <Input disabled={field.name < seniorConfig.length} maxLength={50} />
                                    </Form.Item>
                                  </Col>
                                  <Col flex={1}>
                                    <Form.Item
                                      {...field}
                                      name={[field.name, 'value']}
                                      fieldKey={[field.fieldKey, 'value']}
                                      rules={[
                                      ]}
                                    >
                                      {seniorConfig[field.name] && typeof seniorConfig[field.name].value === 'number' ?
                                        <InputNumber maxLength={20} style={{ minWidth: '100%' }} /> : <Input allowClear maxLength={100} />}
                                    </Form.Item>
                                  </Col>
                                </Row>
                              ))}
                            </div>
                          </div>
                        </>
                      )}
                    </Form.List>
                  </Form.Item>
                </Card> : null}
            </Form>
            <div>
              {renderUploadBtn()}
              <Button type="primary"
                disabled={!url}
                icon={<NoXlmxIcon className={styles.modelIcon} />}
                style={{ marginLeft: 20 }}
                onClick={() => onFinish()}
              >
                {t("breadcrumbs.model.verify")}
              </Button>
            </div>
          </Col>
        </Row>
      </Card>
    </div>
  )
}

const actions = (dispatch) => ({
  getModel(id, force) {
    return dispatch({
      type: 'model/getModel',
      payload: { id, force },
    })
  },
  verify(payload) {
    return dispatch({
      type: 'model/verify',
      payload,
    })
  },
})

export default connect(null, actions)(Verify)
