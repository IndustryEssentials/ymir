import { useEffect, useState, useRef, FC } from 'react'
import { Col, Popover, Row, Space } from 'antd'

import { percent } from '@/utils/number'
import t from '@/utils/t'
import { AnnotationType, evaluationLabel } from '@/constants/dataset'
import { encode, decode, decodeRle } from '@/utils/rle'

import styles from './common.less'

import TestImage from '@/assets/2468fda8-zurich_000110_000019_leftImg8bit.png'
import Mask from './Mask'
import Polygon from './Polygon'

type Props = {
  asset: YModels.Asset
}

const Segmentation: FC<Props> = ({ asset }) => {
  const [annotations, setAnnotations] = useState<YModels.SegAnnotation[]>([])
  const imgContainer = useRef<HTMLDivElement>(null)
  const img = useRef<HTMLImageElement>(null)
  const [width, setWidth] = useState(0)
  const [imgWidth, setImgWidth] = useState(0)
  const [ratio, setRatio] = useState(1)
  const [canvas, setCanvas] = useState<HTMLCanvasElement>()

  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    if (!asset) {
      return
    }
    transAnnotations(asset)
  }, [asset])

  useEffect(() => {
    if (canvasRef.current) {
      setCanvas(canvasRef.current)
    }
  }, [canvasRef])

  function transAnnotations(asset: YModels.Asset) {
    const { width, height, annotations } = asset
    const annos = annotations.map((annotation) => {
      return annotation.type === AnnotationType.Mask
        ? {
            ...annotation,
            decodeMask: decode(annotation.mask, height),
          }
        : annotation
    }) as YModels.SegAnnotation[]

    setAnnotations(annos)
  }

  function calClientWidth() {
    const { current } = imgContainer
    const cw = current?.clientWidth || 0
    const iw = asset.width || 0
    const clientWidth = iw > cw ? cw : iw
    setImgWidth(clientWidth)
    setWidth(cw)
    setRatio(clientWidth / iw)
  }

  function renderAnnotation(annotation: YModels.SegAnnotation) {
    return YModels.AnnotationType.Mask === annotation.type ? <Mask annotation={annotation} /> : <Polygon annotation={annotation} />
  }

  window.addEventListener('resize', () => {
    if (imgContainer.current) {
      calClientWidth()
    }
  })

  return (
    <div className={styles.anno_panel} ref={imgContainer}>
      <div className={styles.img_container}>
        <img ref={img} src={TestImage} style={{ width: imgWidth }} className={styles.assetImg} onLoad={calClientWidth} />
      </div>
      <div className={styles.annotations} style={{ width: imgWidth, left: -imgWidth / 2 }}>
        {annotations.map(renderAnnotation)}
      </div>
    </div>
  )
}

export default Segmentation
