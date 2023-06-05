import { FC, useEffect, useRef, useState } from 'react'
import { renderPolygons } from './_helper'
import { Polygon as PolygonType } from '@/constants'

type Props = {
  annotations: PolygonType[]
  ratio?: number
  simple?: boolean
}

const Polygon: FC<Props> = ({ annotations, ratio = 1, simple }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [canvas, setCanvas] = useState<HTMLCanvasElement>()
  useEffect(() => {
    if (canvasRef.current) {
      setCanvas(canvasRef.current)
    }
  }, [canvasRef.current])

  useEffect(() => {
    if (annotations.length && canvas) {
      renderPolygons(canvas, annotations, !simple, ratio)
    }
  }, [annotations, canvas])

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'absolute',
        left: 0,
        transformOrigin: 'left top 0',
        transform: `scale(${ratio})`,
      }}
      width={annotations[0]?.width}
      height={annotations[0]?.height}
    ></canvas>
  )
}

export default Polygon
