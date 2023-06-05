import { FC, useEffect, useRef, useState } from 'react'
import { renderPolygons } from './_helper'
import { Polygon as PolygonType } from '@/constants'

type Props = {
  annotations: PolygonType[]
  ratio?: number
  simple?: boolean
  width?: number
  height?: number
}

const Polygon: FC<Props> = ({ annotations, ratio = 1, width, height, simple }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [canvas, setCanvas] = useState<HTMLCanvasElement>()
  useEffect(() => {
    if (canvasRef.current) {
      setCanvas(canvasRef.current)
    }
  }, [canvasRef.current])

  useEffect(() => {
    if (annotations.length && canvas && width && height) {
      renderPolygons(canvas, annotations, !simple, ratio)
    }
  }, [annotations, canvas, width, height])

  return (
    <canvas
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
  )
}

export default Polygon
