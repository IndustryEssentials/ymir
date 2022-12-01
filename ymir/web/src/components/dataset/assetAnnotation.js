import { useEffect, useState, useRef } from 'react'
import { Col, Popover, Row, Space } from 'antd'

import { percent } from '@/utils/number'
import t from '@/utils/t'
import { evaluationLabel } from '@/constants/dataset'

import styles from './common.less'

import { encode, decode, decodeRle } from '@/utils/rle'

import TestImage from '@/assets/2468fda8-zurich_000110_000019_leftImg8bit.png'
import test_counts from './mock.json'
const MockData = {
  categories: [
    {
      name: 'car',
      id: 1,
    },
  ],
  images: [
    {
      id: 'image_id',
      width: 1080,
      height: 1350,
      file_name: '/home/jingyi/Developer/cocoapi/2MASK/2468fda8-zurich_000110_000019_leftImg8bit.png',
    },
  ],
  annotations: [
    {
      segmentation: {
        counts: 'US_3e0WY1d0A:F:F;E=D;D:G8G9H7H8I7I6J7H7I8I6J7I7K5K6I6K4L4L3M3N2M3M3M4L3M4K5L3M4L3M3N2M3L5L4L4L4L3M4L3M3N2M3M4L3M4L4L3M3M3M3N2M3N2M3M4L4L3M4L3M3N2M2O2M2O2N2M2O2M2N3M3N2M2O2M2O2M2N3M2N3M2N3N1O2M2O1N3M2M3N2N3M2N2O2M2N3M2N3N1N3M3M2N3N2M2O2N1O2M2O2M2O1O1N3N1O1O1O1O1O1N2N2M3N2M3M3N2M3N2N2N2M3N2N2N101N2O1O1N2O1O1O1O1O1O1N2O1O1O10O01O1O1O1O1O100O1O1O100O1O001O1N2M3O100O1O100O010O1O1O1N2O1N2N1100000000000000000000O10000000000000000O1000000000000O100000000O100000000000000000000O100000000000000000000001O0000000000001O000000001O0000000000001O000000001O0000001O000000001O000000000000001O000000001O000000001O000000001O000000001O0000000002N2N2N3M4L2N1O1N2O00001O000O1000000O100000000000000O1000000000000O01000000O0100000O0100000O0100000O0100000O0100000000000O1000O11O00000O10001O0000001N101O00001O0O2O001O001O000O2O001O00001O000O2O00001O001O1O001O1O1O1O1O1O2N1O1O1O1O1O1O1N2O2N1O1O1O1O1O1O1O001O001O1O1O1O2O1PYO^]OXf0cb0eYO`]OZf0ab0cYOb]O\f0_b0cYOb]O\f0_b0bYOc]O]f0^b0aYOd]O^f0]b0^YOg]Oaf0ob001O001O001O0010O000000001O0O101O0000001N101O00001N101O001O0O10001O00000O101O00000O2O000O101O000O2O000O2O0O2O001N2O0O2O1N2O1N101N101N101N101N1O2O0O2O0O2O0O2N1O2O1N1O2O1N1O2N2O1N1O2O1N1O2O1N101N1O2O1N1O2N2N2N2N2N1O2N101N1O100O2N100O2N100O1O2M2O2M2O2N1O2N101N1O1O2O0O2M2O2N2N1O2N101N1O2O0O2N100O2O000O2O0O2M2O2M2O2N1O2O0O2N2O0O2N2L4L3N3N2N2N1O2N2O0O2L3M4L4M2O2M3N1N3N2M3M3L4M3M3M3M2O2N2N2N2N1N3N2L4M3M3N3L3N2N2N2O1K5L4L4M3N2N3L3M3N2M3M3M3M3M3N2M3M3M3N3L3N2L5K4L5K4L5M3L3M4K4L5K4M4L3M4K4L5K5L4K4M4L4K5L4K5K5J7I6J6J7I6H9F9H9H8H8G:G9G:G9F;Al0mNWZZ;',
        test_counts,
        size: [2048, 1024],
      },
      bbox: [0.0, 0.0, 361.0, 2048.0],
      area: 368961,
      image_id: 'image_id',
      category_id: 1,
      iscrowd: 0,
      id: 23,
    },
  ],
}

function AssetAnnotation({ url, data = [] }) {
  const [annotations, setAnnotations] = useState([])
  const imgContainer = useRef()
  const img = useRef()
  const [width, setWidth] = useState(0)
  const [imgWidth, setImgWidth] = useState(0)
  const [ratio, setRatio] = useState(1)
  const [canvas, setCanvas] = useState(null)

  const canvasRef = useRef()

  useEffect(() => {
    // transAnnotations(data)
    transSegAnnotations(MockData)
  }, [data])

  useEffect(() => {
    if (canvasRef.current) {
      setCanvas(canvasRef.current)
    }
  }, [canvasRef])

  useEffect(() => {
    if (annotations.length && imgWidth) {
      const testAnnotation = annotations[0]
      renderMask(testAnnotation.mask, testAnnotation.image.width, testAnnotation.image.height)
    }
  }, [annotations, imgWidth])

  function transSegAnnotations({ categories = [], images = [], annotations }) {
    const annos = annotations.map(({ segmentation, image_id }) => {
      const imageInfo = images.find(({ id }) => id === image_id)
      const mask = decode(segmentation.counts, imageInfo.height)
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

  function calImgWidth(target) {
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
      {/* <div>
        <img src={TestImage} />
      </div> */}
    </div>
  )
}

export default AssetAnnotation
