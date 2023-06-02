import { Mask as MaskType } from '@/constants'
import { FC, useEffect, useRef, useState } from 'react'
import { renderMasks } from './_helper'

type Props = {
  annotations: MaskType[]
  ratio?: number
  simple?: boolean
  width?: number
  height?: number
}

const Mask: FC<Props> = ({ annotations, ratio = 1, width, height, simple }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [canvas, setCanvas] = useState<HTMLCanvasElement>()

  useEffect(() => {
    if (canvasRef.current) {
      setCanvas(canvasRef.current)
    }
  }, [canvasRef.current])

  useEffect(() => {
    if (annotations.length && canvas && width && height) {
      renderMasks(canvas, annotations, !simple)
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

export default Mask
