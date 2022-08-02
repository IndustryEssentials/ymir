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

  const renderAnnotations = () => filters(annotations).map((annotation, index) => <div
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
  ></div>)

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
  let calculating = false
  window.addEventListener('resize', () => {
    if (calculating) return
    calculating = true
    window.setTimeout(() => {
    if (img.current) {
      calImgWidth()
    }
    calculating = false
    }, 2000)
  })

  return (
    <div className={styles.ic_container}>
      <img
        ref={img}
        src={url}
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
