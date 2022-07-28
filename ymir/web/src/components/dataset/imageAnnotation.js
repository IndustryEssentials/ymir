import styles from "./common.less"
import { useEffect, useState, useRef } from "react"

function ImageAnnotation({
  url,
  data = [],
  filters = a => a,
}) {
  const [annotations, setAnnotations] = useState([])
  const img = useRef()
  const [box, setBox] = useState({
    width: 0,
    height: 0,
  })
  const [ratio, setRatio] = useState(1)

  useEffect(() => {
    transAnnotations(data)
  }, [data])

  const transAnnotations = (items) => {
    setAnnotations(() => {
      return items.map(({ box, score, ...item }) => {
        return {
          ...item,
          ...box,
        }
      })
    })
  }

  const renderAnnotations = () => {
    return filters(annotations).map((annotation, index) => {
      return (
        <div
          title={`${annotation.keyword}` + (annotation.score ? `\nConference:${annotation.score}` : '')}
          className={`${styles.annotation} ${annotation.gt ? styles.gt : ''}`}
          key={index}
          style={{
            position: 'absolute',
            color: annotation.color,
            borderColor: annotation.color,
            boxShadow: `${annotation.color} 0 0 2px 1px`,
            top: annotation.y * ratio,
            left: annotation.x * ratio,
            width: annotation.w * ratio - 2,
            height: annotation.h * ratio - 2,
          }}
        ></div>
      )
    })
  }

  function calImgWidth(target) {
    const im = target || img.current
    if (!im) {
      return
    }
    const cw = im.clientWidth
    const iw = im.naturalWidth || 0
    setBox({
      width: cw,
      height: im.clientHeight,
    })
    setRatio(cw / iw)
  }

  window.addEventListener('resize', () => {
    if (img.current) {
      calImgWidth()
    }
  })

  return (
    <div className={styles.annotations} style={{
      position: 'relative',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100%',
      width: '100%',
    }}>
      <img
        ref={img}
        src={url}
        style={{ maxWidth: '100%', maxHeight: '100%' }}
        className={styles.assetImg}
        onLoad={({ target }) => calImgWidth()}
      />
      <div style={{
        position: 'absolute',
        top: 0,
        left: '50%',
        marginLeft: -(box.width / 2),
        width: box.width,
        height: box.height,
        zIndex: 5,
      }}>
        {renderAnnotations()}
      </div>
    </div>
  )
}

export default ImageAnnotation
