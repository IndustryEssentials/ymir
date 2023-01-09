import { useEffect, useState, useRef, FC } from 'react'

import { AnnotationType } from '@/constants/dataset'
import { transferAnnotations } from './_helper'

import Mask from './Mask'
import Polygon from './Polygon'
import BoundingBox from './BoundingBox'

import styles from '../common.less'

type Props = {
  asset: YModels.Asset
}

const AssetAnnotation: FC<Props> = ({ asset }) => {
  const [annotations, setAnnotations] = useState<YModels.Annotation[]>([])
  const imgContainer = useRef<HTMLDivElement>(null)
  const img = useRef<HTMLImageElement>(null)
  const [width, setWidth] = useState(0)
  const [imgWidth, setImgWidth] = useState(0)
  const [ratio, setRatio] = useState(1)

  useEffect(() => {
    if (!asset) {
      return
    }
    const updateAnnotations = transferAnnotations(asset.annotations, asset)
    setAnnotations(updateAnnotations)
  }, [asset])

  function calClientWidth() {
    const { current } = imgContainer
    const cw = current?.clientWidth || 0
    const iw = asset?.width || 0
    const clientWidth = iw > cw ? cw : iw
    setImgWidth(clientWidth)
    setWidth(cw)
    setRatio(clientWidth / iw)
  }

  function renderAnnotation(annotation: YModels.Annotation, key: number) {
    switch (annotation.type) {
      case AnnotationType.BoundingBox:
        return <BoundingBox key={key} annotation={annotation} ratio={ratio} />
      case AnnotationType.Polygon:
        return <Polygon key={key} annotation={annotation} ratio={ratio} />
      case AnnotationType.Mask:
        return <Mask key={key} annotation={annotation} ratio={ratio} />
    }
  }

  window.addEventListener('resize', () => {
    if (imgContainer.current) {
      calClientWidth()
    }
  })

  return (
    <div className={styles.anno_panel} ref={imgContainer} key={asset?.hash}>
      <div className={styles.img_container}>
        <img ref={img} src={asset?.url} style={imgWidth ? { width: imgWidth } : undefined} className={styles.assetImg} onLoad={calClientWidth} />
      </div>
      <div className={styles.annotations} style={{ width: imgWidth, left: -imgWidth / 2 }}>
        {annotations.map(renderAnnotation)}
      </div>
    </div>
  )
}

export default AssetAnnotation
