import { useEffect, useState, useRef, FC } from 'react'

import { AnnotationType } from '@/constants/asset'
import { transferAnnotations } from './asset/_helper'

import Mask from './asset/Mask'
import Polygon from './asset/Polygon'
import BoundingBox from './asset/BoundingBox'

import styles from './common.less'
import { useDebounceEffect } from 'ahooks'
import { Annotation, Asset, BoundingBox as BoundingBoxType, Polygon as PolygonType, Mask as MaskType } from '@/constants'

type Props = {
  asset: Asset
  filter?: (annotations: Annotation[]) => Annotation[]
  hideAsset?: boolean
  isFull?: boolean
}

const ListAnnotation: FC<Props> = ({ asset, filter, hideAsset, isFull }) => {
  const [annotations, setAnnotations] = useState<Annotation[]>([])
  const imgContainer = useRef<HTMLDivElement>(null)
  const img = useRef<HTMLImageElement>(null)
  const [width, setWidth] = useState(0)
  const [imgWidth, setImgWidth] = useState(100)
  const [ratio, setRatio] = useState(1)

  const [bbA, setBbA] = useState<BoundingBoxType[]>([])
  const [pgA, setPgA] = useState<PolygonType[]>([])
  const [maA, setMaA] = useState<MaskType[]>([])

  useEffect(() => {
    setBbA(filterAts(AnnotationType.BoundingBox) as BoundingBoxType[])
    setPgA(filterAts(AnnotationType.Polygon) as PolygonType[])
    setMaA(filterAts(AnnotationType.Mask) as MaskType[])
  }, [annotations])

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
    const clientWidth = isFull ? cw : iw > cw ? cw : iw
    setImgWidth(clientWidth)
    setWidth(cw)
    setRatio(clientWidth / iw)
  }

  window.addEventListener('resize', () => imgContainer.current && calClientWidth())

  const filterAts = (fType: AnnotationType) => annotations?.filter(({ type }) => fType === type)

  return (
    <div className={styles.ic_container} ref={imgContainer}>
      <img ref={img} style={{ visibility: hideAsset ? 'hidden' : 'visible' }} src={asset?.url} className={styles.assetImg} onLoad={calClientWidth} />
      <div className={styles.annotations} style={{ width: imgWidth, left: -imgWidth / 2 }}>
        {bbA.length ? bbA.map((anno) => <BoundingBox key={anno.id} annotation={anno} ratio={ratio} simple={true} />) : null}
        {pgA.length ? <Polygon annotations={pgA} ratio={ratio} simple={true} /> : null}
        {maA.length ? maA.map((anno) => <Mask key={anno.id} annotation={anno} ratio={ratio} simple={true} />) : null}
      </div>
    </div>
  )
}

export default ListAnnotation
