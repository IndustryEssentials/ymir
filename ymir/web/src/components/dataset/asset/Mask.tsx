import { Mask as MaskType } from '@/constants'
import { FC, useEffect, useRef, useState } from 'react'
import { renderMask } from './_helper'

type Props = {
  annotation: MaskType
  ratio?: number
  simple?: boolean
  width?: number
  height?: number
}

const Mask: FC<Props> = ({ annotation, ratio = 1, width, height, simple }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [canvas, setCanvas] = useState<HTMLCanvasElement>()

  useEffect(() => {
    if (canvasRef.current) {
      setCanvas(canvasRef.current)
    }
  }, [canvasRef.current])

  useEffect(() => {
    if (annotation && canvas && width && height) {
      renderMask(canvas, annotation, !simple, ratio)
    }
  }, [annotation, canvas, width, height])

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
