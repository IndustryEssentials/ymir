import { useEffect, useState, useRef } from "react"
import { Col, Popover, Row, Space } from "antd"

import { percent } from "@/utils/number"
import t from '@/utils/t'
import { evaluationLabel } from '@/constants/dataset'

import styles from "./common.less"

function AssetAnnotation({
  url,
  data = [],
}) {
  const [annotations, setAnnotations] = useState([])
  const imgContainer = useRef()
  const img = useRef()
  const [width, setWidth] = useState(0)
  const [imgWidth, setImgWidth] = useState(0)
  const [ratio, setRatio] = useState(1)

  useEffect(() => {
    transAnnotations(data)
  }, [data])

  const transAnnotations = (items) => {
    setAnnotations(() => {
      return items.map(({ box, score, ...item }) => {
        return {
          ...item,
          score: score ? percent(score) : null,
          ...box,
        }
      })
    })
  }

  const renderAnnotations = () => {
    return annotations.map((annotation, index) => {
      const evaluatedLabel = evaluationLabel(annotation.cm)
      const emptyTags = Object.keys(annotation.tags).length === 0
      const popContent = <>
        <Row><Col flex={'100px'}>{t('keyword.column.name')}</Col><Col flex={1}>{annotation.keyword}</Col></Row>
        {evaluatedLabel ? <Row><Col flex={'100px'}>Evaluation</Col><Col flex={1}>{evaluationLabel(annotation.cm)}</Col></Row> : null}
        {annotation.score ? <Row><Col flex={'100px'}>{t('model.verify.confidence')}</Col><Col flex={1}>{annotation.score}</Col></Row> : null}
        {!emptyTags ? <Row><Col flex={'100px'}>{t('dataset.assets.keyword.selector.types.tags')}</Col><Col flex={1}>
          {Object.keys(annotation.tags).map(tag => <Space key={tag} style={{ width: '100%' }}>
            <span style={{ fontWeight: 'bold' }}>{tag}: </span> <span>{annotation.tags[tag]}</span>
          </Space>)}
        </Col>
        </Row> : null}
      </>
      return <Popover key={index} content={popContent} placement='right'>
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
          <span className={styles.annotationTitle} style={{ backgroundColor: annotation.color }}>{annotation.keyword}
            {annotation.score ? <> {annotation.score}</> : null}</span>
        </div>
      </Popover>
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
        <img
          ref={img}
          src={url}
          style={{ width: imgWidth }}
          className={styles.assetImg}
          onLoad={({ target }) => calImgWidth(target)}
        />
      </div>
      <div className={styles.annotations} style={{ width: imgWidth, left: -imgWidth / 2 }}>
        {renderAnnotations()}
      </div>
    </div>
  )
}

export default AssetAnnotation
