import { useEffect, useState, useRef, FC } from 'react'
import { Col, Popover, Row, Space } from 'antd'

import { percent } from '@/utils/number'
import t from '@/utils/t'
import { evaluationLabel } from '@/constants/dataset'
import { encode, decode, decodeRle } from '@/utils/rle'

import styles from './common.less'

import MockData from './mockData'
import TestImage from '@/assets/2468fda8-zurich_000110_000019_leftImg8bit.png'

type Props = {
  image: string,
  annotations: YModels.SegAnnotation[],
}

const Segmentation: FC<Props> = ({ image, annotations = [] }) => {
  const [segAnnotations, setAnnotations] = useState([])
  const imgContainer = useRef<HTMLElement>()
  const img = useRef<HTMLImageElement>()
  const [width, setWidth] = useState(0)
  const [imgWidth, setImgWidth] = useState(0)
  const [ratio, setRatio] = useState(1)
  const [canvas, setCanvas] = useState<HTMLCanvasElement>()

  const canvasRef = useRef()

  useEffect(() => {
    // transAnnotations(data)
    transSegAnnotations(MockData)
  }, [annotations])

  useEffect(() => {
    if (canvasRef.current) {
      setCanvas(canvasRef.current)
    }
  }, [canvasRef])

  useEffect(() => {
    if (annotations.length && imgWidth) {
      const testAnnotation = annotations[0]
      if (testAnnotation.type === YModels.AnnotationType.Mask) {
        renderMask(testAnnotation.mask, testAnnotation.image.width, testAnnotation.image.height)
      }
    }
  }, [annotations, imgWidth])

  function transSegAnnotations({ categories = [], images = [], annotations }) {
    const annos = annotations.map(({ segmentation, image_id }) => {
      const imageInfo = images.find(({ id }) => id === image_id)
      const mask = decode(segmentation.counts, 1350)
      console.log('mask:', mask, segmentation.counts)
      // const mask = decodeRle(segmentation.test_counts, 1024)
      // const mask = segmentation.test_counts
      return {
        type: 'mask',
        mask,
        rect: segmentation.size,
        image: imageInfo,
      }
    })

    setAnnotations(annos)
  }

  function renderMask(mask, nw, nh) {
    console.log('mask:', mask)
    if (!canvas) {
      return
    }
    const ctx = canvas.getContext('2d')

    canvas.width = nw
    canvas.height = nh

    const trueWidth = mask[0].length

    const dataWithColor = mask.map(row => row.map(col => col ? [255, 0, 0, 160] : [0, 0, 0, 0])).flat().flat()
    const imageData = Uint8ClampedArray.from(dataWithColor)
    // console.log('imageData:', imageData, dataWithColor)
    const image = new ImageData(imageData, trueWidth, nh)
    console.log('image:', image)
    // const newdata = ctx.createImageData(nw, nh)
    // newdata.data.set(mask)

    ctx.putImageData(image, 0, 0)
  }

  function renderImage(image) {
    if (!canvas) {
      return
    }
    const ctx = canvas.getContext('2d')
  }

  const transAnnotations = (items) => {
    setAnnotations(() => {
      return items.map(({ box, score, ...item }) => {
        return {
          ...item,
          score: score ? percent(score) : null,
          ...box,
          type: 'box',
        }
      })
    })
  }

  const renderAnnotations = () => {
    return annotations.map((annotation, index) => {
      const evaluatedLabel = evaluationLabel(annotation.cm)
      const emptyTags = Object.keys(annotation.tags).length === 0
      const popContent = (
        <>
          <Row>
            <Col flex={'100px'}>{t('keyword.column.name')}</Col>
            <Col flex={1}>{annotation.keyword}</Col>
          </Row>
          {evaluatedLabel ? (
            <Row>
              <Col flex={'100px'}>Evaluation</Col>
              <Col flex={1}>{evaluationLabel(annotation.cm)}</Col>
            </Row>
          ) : null}
          {annotation.score ? (
            <Row>
              <Col flex={'100px'}>{t('model.verify.confidence')}</Col>
              <Col flex={1}>{annotation.score}</Col>
            </Row>
          ) : null}
          {!emptyTags ? (
            <Row>
              <Col flex={'100px'}>{t('dataset.assets.keyword.selector.types.tags')}</Col>
              <Col flex={1}>
                {Object.keys(annotation.tags).map((tag) => (
                  <Space key={tag} style={{ width: '100%' }}>
                    <span style={{ fontWeight: 'bold' }}>{tag}: </span> <span>{annotation.tags[tag]}</span>
                  </Space>
                ))}
              </Col>
            </Row>
          ) : null}
        </>
      )
      return (
        <Popover key={index} content={popContent} placement="right">
          <div
            title={`${annotation.keyword}` + (annotation.score ? `\nConference:${annotation.score}` : '')}
            className={`${styles.annotation} ${annotation.gt ? styles.gt : ''}`}
            key={index}
            style={{
              color: annotation.color,
              borderColor: annotation.color,
              boxShadow: `${annotation.color} 0 0 2px 1px`,
              top: annotation.y * ratio,
              left: annotation.x * ratio,
              width: annotation.w * ratio - 2,
              height: annotation.h * ratio - 2,
            }}
          >
            <span className={styles.annotationTitle} style={{ backgroundColor: annotation.color }}>
              {annotation.keyword}
              {annotation.score ? <> {annotation.score}</> : null}
            </span>
          </div>
        </Popover>
      )
    })
  }

  function calImgWidth(target: EventTarget) {
    const im = target || img.current
    const { current } = imgContainer
    const cw = current.clientWidth
    const iw = im.naturalWidth || 0
    const clientWidth = iw > cw ? cw : iw
    setImgWidth(clientWidth)
    setWidth(cw)
    setRatio(clientWidth / iw)
  }

  window.addEventListener('resize', () => {
    if (imgContainer.current) {
      calImgWidth()
    }
  })

  return (
    <div className={styles.anno_panel} ref={imgContainer}>
      <div className={styles.img_container}>
        <img ref={img} src={TestImage} style={{ width: imgWidth }} className={styles.assetImg} onLoad={({ target }) => calImgWidth(target)} />
      </div>
      <div className={styles.annotations} style={{ width: imgWidth, left: -imgWidth / 2 }}>
        {/* {renderAnnotations()} */}
        <canvas ref={canvasRef}></canvas>
      </div>
    </div>
  )
}

export default Segmentation
