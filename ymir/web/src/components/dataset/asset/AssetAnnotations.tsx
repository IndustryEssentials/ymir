import { useEffect, useState, useRef, FC, SyntheticEvent } from 'react'

import { AnnotationType } from '@/constants/asset'
import { transferAnnotations } from './_helper'

import Mask from './Mask'
import Polygon from './Polygon'
import BoundingBox from './BoundingBox'

import styles from '../common.less'
import { Annotation, BoundingBox as BoundingBoxType, Mask as MaskType, Polygon as PolygonType } from '@/constants'

export type Asset = {
  annotations: Annotation[]
  hash?: string
  url?: string
  width?: number
  height?: number
}
type Props = {
  asset: Asset
}

const AssetAnnotation: FC<Props> = ({ asset }) => {
  const [annotations, setAnnotations] = useState<Annotation[]>([])
  const imgContainer = useRef<HTMLDivElement>(null)
  const img = useRef<HTMLImageElement>(null)
  const [width, setWidth] = useState(0)
  const [imgWidth, setImgWidth] = useState(0)
  const [ratio, setRatio] = useState(1)

  useEffect(() => {
    if (!asset) {
      return
    }
    let annos = asset.annotations
    if (annos?.length && !asset?.height && img.current) {
      const { naturalWidth, naturalHeight } = img.current
      annos = annos.map((anno) => ({
        ...anno,
        height: naturalHeight,
        width: naturalWidth,
      }))
    }
    setAnnotations(transferAnnotations(annos))
  }, [asset, img.current])

  function calClientWidth(imgWidth?: number) {
    const { current } = imgContainer
    const cw = current?.clientWidth || 0
    const iw = asset?.width || width || imgWidth || 0
    const clientWidth = iw > cw ? cw : iw
    setImgWidth(clientWidth)
    setWidth(iw)
    setRatio(clientWidth / iw)
  }

  const Annotations: FC<{ annotations: Annotation[] }> = ({ annotations }) => {
    const filterAts = (fType: AnnotationType) => annotations.filter(({ type }) => fType === type)
    const bbA = filterAts(AnnotationType.BoundingBox) as BoundingBoxType[]
    const pgA = filterAts(AnnotationType.Polygon) as PolygonType[]
    const maA = filterAts(AnnotationType.Mask) as MaskType[]

    return (
      <>
        {bbA.map((anno) => (
          <BoundingBox key={anno.id} annotation={anno} ratio={ratio} />
        ))}
        <Polygon annotations={pgA} width={asset.width} height={asset.height} ratio={ratio} />
        <Mask annotations={maA} width={asset.width} height={asset.height} ratio={ratio} />
      </>
    )
  }

  const imgLoad = (e: SyntheticEvent) => {
    if (img.current && img.current.naturalWidth) {
      const { naturalWidth } = img.current
      calClientWidth(naturalWidth)
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
        <img ref={img} src={asset?.url} style={imgWidth ? { width: imgWidth } : undefined} className={styles.assetImg} onLoad={imgLoad} />
      </div>
      <div className={styles.annotations} style={{ width: imgWidth, left: -imgWidth / 2 }}>
        <Annotations annotations={annotations} />
      </div>
    </div>
  )
}

export default AssetAnnotation
