import { FC, useEffect, useRef, useState } from 'react'
import { renderPolygon } from './_helper'
type Props = {
  annotation: YModels.Polygon,
  ratio?: number,
  simple?: boolean
}

const Polygon: FC<Props> = ({ annotation, ratio = 1 }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [canvas, setCanvas] = useState<HTMLCanvasElement>()
  const [{ width, height }, setRect] = useState({
    width: 0,
    height: 0,
  })
  useEffect(() => {
    if (canvasRef.current) {
      setCanvas(canvasRef.current)
    }
  }, [canvasRef.current])

  useEffect(() => {
    if (annotation.polygon?.length && canvas) {
      renderPolygon(canvas, annotation.polygon, annotation.color)
    }
  }, [annotation.polygon, canvas, width, height])

  useEffect(() => {
    if (!annotation) {
      return
    }
    setRect({
      width: annotation.width,
      height: annotation.height,
    })
  }, [annotation])

  return <canvas
    ref={canvasRef}
    style={{
      position: 'absolute',
      left: 0,
      transformOrigin: 'left top 0',
      transform: `scale(${ratio})`,
    }}
    width={width}
    height={height}
  ></canvas>
}

export default Polygon
