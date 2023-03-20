import { useEffect, useState, useRef, FC } from 'react'

import { AnnotationType } from '@/constants/dataset'
import { transferAnnotations } from './asset/_helper'

import Mask from './asset/Mask'
import Polygon from './asset/Polygon'
import BoundingBox from './asset/BoundingBox'

import styles from './common.less'
import { useDebounceEffect } from 'ahooks'

type Props = {
  asset: YModels.Asset
  filter?: (annotations: YModels.Annotation[]) => YModels.Annotation[]
  hideAsset?: boolean
  isFull?: boolean
}

const ListAnnotation: FC<Props> = ({ asset, filter, hideAsset, isFull }) => {
  const [annotations, setAnnotations] = useState<YModels.Annotation[]>([])
  const imgContainer = useRef<HTMLDivElement>(null)
  const img = useRef<HTMLImageElement>(null)
  const [width, setWidth] = useState(0)
  const [imgWidth, setImgWidth] = useState(100)
  const [ratio, setRatio] = useState(1)

  useDebounceEffect(
    () => {
      if (!asset) {
        return
      }
      const updateAnnotations = transferAnnotations(asset.annotations)
      setAnnotations(filter ? filter(updateAnnotations) : updateAnnotations)
    },
    [asset, filter],
    { wait: 10 },
  )

  function calClientWidth() {
    const { current } = imgContainer
    const cw = current?.clientWidth || 0
    const iw = asset?.width || 0
    const clientWidth = isFull? cw : (iw > cw ? cw : iw)
    setImgWidth(clientWidth)
    setWidth(cw)
    setRatio(clientWidth / iw)
  }

  window.addEventListener('resize', () => imgContainer.current && calClientWidth())

  function renderAnnotation(annotation: YModels.Annotation) {
    switch (annotation.type) {
      case AnnotationType.BoundingBox:
        return <BoundingBox key={annotation.id} annotation={annotation} ratio={ratio} simple={true} />
      case AnnotationType.Polygon:
        return <Polygon key={annotation.id} annotation={annotation} ratio={ratio} simple={true} />
      case AnnotationType.Mask:
        return <Mask key={annotation.id} annotation={annotation} ratio={ratio} simple={true} />
    }
  }

  return (
    <div className={styles.ic_container} ref={imgContainer} key={asset.hash}>
      <img ref={img} style={{ visibility: hideAsset ? 'hidden' : 'visible' }} src={asset?.url} className={styles.assetImg} onLoad={calClientWidth} />
      <div className={styles.annotations} style={{ width: imgWidth, left: -imgWidth / 2 }}>
        {annotations.map(renderAnnotation)}
      </div>
    </div>
  )
}

export default ListAnnotation
