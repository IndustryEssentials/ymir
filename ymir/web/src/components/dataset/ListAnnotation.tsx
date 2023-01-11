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
}

const ListAnnotation: FC<Props> = ({ asset, filter }) => {
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
      const updateAnnotations = transferAnnotations(asset.annotations, asset)
      setAnnotations(filter ? filter(updateAnnotations) : updateAnnotations)
    },
    [asset, filter],
    { wait: 10 },
  )

  function calClientWidth() {
    const { current } = imgContainer
    const cw = current?.clientWidth || 0
    const iw = asset?.width || 0
    const clientWidth = iw > cw ? cw : iw
    setImgWidth(clientWidth)
    setWidth(cw)
    setRatio(clientWidth / iw)
  }

  function renderAnnotation(annotation: YModels.Annotation, key: number | string) {
    switch (annotation.type) {
      case AnnotationType.BoundingBox:
        return <BoundingBox key={key} annotation={annotation} ratio={ratio} simple={true} />
      case AnnotationType.Polygon:
        return <Polygon key={key} annotation={annotation} ratio={ratio} simple={true} />
      case AnnotationType.Mask:
        return <Mask key={key} annotation={annotation} ratio={ratio} simple={true} />
    }
  }

  window.addEventListener('resize', () => {
    if (imgContainer.current) {
      calClientWidth()
    }
  })

  return (
    <div className={styles.ic_container} ref={imgContainer} key={asset.hash}>
      <img ref={img} src={asset?.url} className={styles.assetImg} onLoad={calClientWidth} />
      <div className={styles.annotations} style={{ width: imgWidth, left: -imgWidth / 2 }}>
        {annotations.map((anno, index) => renderAnnotation(anno, asset.hash + index))}
      </div>
    </div>
  )
}

export default ListAnnotation
