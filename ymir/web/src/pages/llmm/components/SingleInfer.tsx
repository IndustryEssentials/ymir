import { FC, useState, useEffect } from 'react'
import { useParams, useSelector } from 'umi'
import t from '@/utils/t'
import { Button, Col, Form, InputNumber, Row, Slider } from 'antd'
import { Annotation, Project } from '@/constants'
import AssetAnnotation, { Asset } from '@/components/dataset/asset/AssetAnnotations'
import { isSemantic, ObjectType } from '@/constants/objectType'
import useRequest from '@/hooks/useRequest'

import styles from '../inference.less'
import ImgDef from '@/assets/img_def.png'
import { NoXlmxIcon } from '@/components/common/Icons'
import Uploader from '@/components/form/uploader'
import { generateDatasetColors } from '@/constants/asset'
import DockerConfigForm from '@/components/form/items/DockerConfig'
import { getConfig, TYPES } from '@/constants/image'
import PromptInput from './PromptInput'
import { transHyperParams } from './_utils'
import GPUCount from '@/components/form/items/GPUCount'

type Props = {}

const SingleInfer: FC<Props> = ({}) => {
  const params = useParams<{ id: string }>()
  const pid = Number(params.id)
  const [virtualAsset, setVirtualAsset] = useState<Asset>({ annotations: [] })
  const IMGSIZELIMIT = 10
  const [confidence, setConfidence] = useState(20)
  const [annotations, setAnnotations] = useState<Annotation[]>([])
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([])
  const [form] = Form.useForm()
  const [seniorConfig, setSeniorConfig] = useState<{ [key: string]: any }>({})
  const { groundedSAM: image } = useSelector(({ image }) => image)
  const { data: verifyResult, run: verify } = useRequest<Annotation[]>('model/verify')
  const { data: project, run: getProject } = useRequest<Project, [{ id: number }]>('project/getProject', {
    cacheKey: 'getProject',
    loading: false,
  })

  const renderUploader = (
    <div className={styles.uploader}>
      <div className={styles.emptyImg}>
        <img src={ImgDef} />
        <p>{t('model.verify.upload.tip')}</p>
        <p>{t('model.verify.upload.info', { size: IMGSIZELIMIT })}</p>
        <Uploader
          key={'uploader'}
          // className={styles.btn}
          onChange={({ file, fileList }) => {
            if (fileList.length) {
              setVirtualAsset({ annotations: [], url: fileList[0].url })
              setAnnotations([])
            }
          }}
          format="img"
          label={t('model.verify.upload.label')}
          showUploadList={false}
          max={IMGSIZELIMIT}
        />
      </div>
    </div>
  )

  useEffect(() => {
    if (!image) {
      return
    }
    const config = getConfig(image, TYPES.INFERENCE, ObjectType.MultiModal)
    config && setSeniorConfig(config.config)
  }, [image])

  useEffect(() => {
    const confidenceFilter = (anno: Annotation) => isSemantic(project?.type) || !anno.score || anno.score * 100 > confidence
    const annos = annotations.length ? annotations.filter((anno) => confidenceFilter(anno) && selectedKeywords.indexOf(anno.keyword) > -1) : []
    setVirtualAsset((asset) => ({ ...asset, annotations: annos }))
  }, [confidence, annotations, selectedKeywords, project?.type])

  useEffect(() => {
    if (verifyResult) {
      const all = verifyResult || []
      const keywords = [...new Set(all.map((anno) => anno.keyword))]
      const colors = generateDatasetColors(keywords)
      setAnnotations(all.map((anno) => ({ ...anno, color: colors[anno.keyword] })))
      all.length && setSelectedKeywords([...new Set(all.map((anno) => anno.keyword))])
    }
  }, [verifyResult])

  useEffect(() => {
    pid && getProject({ id: pid })
  }, [pid])

  const infer = () => {
    if (!image) {
      return
    }
    form
      .validateFields()
      .then(() => {
        const { hyperparam, prompt, gpu_count } = form.getFieldsValue()
        const config = transHyperParams(hyperparam, prompt, gpu_count)

        verify({ projectId: pid, urls: [virtualAsset?.url], image: image?.id, config })
      })
      .catch((err) => {})
  }

  return (
    <Row className={styles.infoRow} wrap={false}>
      <Col span={18} className={`${styles.asset_img} scrollbar`}>
        {virtualAsset?.url ? <AssetAnnotation asset={virtualAsset} /> : renderUploader}
        {virtualAsset?.url && !isSemantic(project?.type) ? (
          <Form className={styles.confidence}>
            <Form.Item label={t('model.verify.confidence')}>
              <Row gutter={10}>
                <Col flex={1}>
                  <Slider
                    marks={{ 0: '0%', 100: '100%' }}
                    style={{ width: 200 }}
                    tipFormatter={(value) => `${value}%`}
                    value={confidence}
                    onChange={setConfidence}
                  />
                </Col>
                <Col>
                  <InputNumber
                    value={confidence}
                    style={{ width: 60, borderColor: 'rgba(0, 0, 0, 0.15)', margin: 5, height: 35 }}
                    precision={0}
                    min={0}
                    max={100}
                    onChange={setConfidence}
                  />
                </Col>
              </Row>
            </Form.Item>
          </Form>
        ) : null}
      </Col>
      <Col span={6} className={`${styles.asset_info} scrollbar`}>
        <Form form={form} className={styles.asset_form}>
          <PromptInput />
          <GPUCount form={form} min={1} />
          <DockerConfigForm form={form} show={true} itemProps={{ wrapperCol: { span: 24 } }} seniorConfig={seniorConfig} />
        </Form>
        <div>
          <Button
            type="primary"
            disabled={!virtualAsset?.url}
            icon={<NoXlmxIcon className={styles.modelIcon} />}
            style={{ marginLeft: 20 }}
            onClick={() => infer()}
          >
            {t('breadcrumbs.model.verify')}
          </Button>
        </div>
      </Col>
    </Row>
  )
}
export default SingleInfer
