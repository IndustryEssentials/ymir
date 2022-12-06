import { useEffect, useState, useRef, FC } from 'react'
import { Col, Popover, Row, Space } from 'antd'

import { percent } from '@/utils/number'
import t from '@/utils/t'
import { evaluationLabel } from '@/constants/dataset'

import styles from './common.less'
import BoundingBox from './BoundingBox'

type Props = {
  asset: YModels.Asset
}

const Detection: FC<Props> = ({ asset }) => {
  const [annotations, setAnnotations] = useState<YModels.DetAnnotation[]>([])
  const imgContainer = useRef()
  const img = useRef<HTMLImageElement>(null)

  useEffect(() => asset && transAnnotations(asset), [asset])

  const transAnnotations = ({ annotations }: YModels.Asset) => {
    
    const items = annotations.map(({ score, ...item }) => {
      return {
        ...item,
        score: score ? percent(score) : null,
      }
    }) as YModels.DetAnnotation[]
  
    setAnnotations(items)
  }

  return (
    <div className={styles.anno_panel} ref={imgContainer}>
      <div className={styles.img_container}>
        <img ref={img} src={asset?.url} style={{ width: imgWidth }} className={styles.assetImg} onLoad={({ target }) => calImgWidth(target)} />
      </div>
      <div className={styles.annotations} style={{ width: imgWidth, left: -imgWidth / 2 }}>
        <BoundingBox annotations={annotations} />
      </div>
    </div>
  )
}

export default Detection
