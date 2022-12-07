import { FC, useEffect, useRef, useState } from 'react'
import { renderPolygon } from './_helper'
type Props = {
  annotation: YModels.Polygon,
  ratio?: number,
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
    if (annotation.points?.length && canvas) {
      renderPolygon(canvas, annotation.points, width, height)
    }
  }, [annotation.points, canvas, width, height])

  useEffect(() => {
    if (!annotation) {
      return
    }
    setRect({
      width: annotation.width * ratio,
      height: annotation.height * ratio,
    })
  }, [annotation, ratio])

  return <canvas
    ref={canvasRef}
    style={{
      transform: `translate(50%, 50%) scale(${ratio})`,
    }}
    width={width}
    height={height}
  ></canvas>
}

export default Polygon
