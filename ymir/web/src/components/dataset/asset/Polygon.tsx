import { FC, useEffect, useRef, useState } from 'react'
import { renderPolygon } from './_helper'
type Props = {
  annotation: YModels.Polygon
}

const Polygon: FC<Props> = ({ annotation }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [canvas, setCanvas] = useState<HTMLCanvasElement>()
  useEffect(() => {
    if (canvasRef.current) {
      setCanvas(canvasRef.current)
    }
  }, [canvasRef.current])

  useEffect(() => {
    if (annotation.points?.length && canvas) {
      renderPolygon(canvas, annotation.points, annotation.width, annotation.height)
    }
  }, [annotation.points, canvas])

  return <canvas ref={canvasRef}></canvas>
}

export default Polygon
