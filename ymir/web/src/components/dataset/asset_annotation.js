import styles from "./common.less"
import { useEffect, useState, useRef } from "react"
import { percent } from "../../utils/number"

function AssetAnnotation({
  url,
  data = [],
  colors = ["green", "red", "cyan", "blue", "yellow", "purple", "magenta", "orange", "gold"],
  keywords = [],
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
      let index = 0
      return items.map(({ keyword, box, score, color = '#000' }) => {
        return {
          keyword,
          score: score ? percent(score) : null,
          color,
          ...box,
        }
      })
    })
  }

  const renderAnnotations = () => {
    // console.log('annotations: ', annotations)
    return annotations.map((annotation, index) => {
      return (
        <div
          title={`${annotation.keyword}` + (annotation.score ? `\nConference:${annotation.score}` : '')}
          className={`${styles.annotation}`}
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
          <span className={styles.annotationTitle} style={{ backgroundColor: annotation.color}}>{annotation.keyword}
          {annotation.score ? <> {annotation.score}</> : null}</span>
        </div>
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
