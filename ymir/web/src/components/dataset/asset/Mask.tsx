import { Mask as MaskType } from '@/constants'
import { FC, useEffect, useRef, useState } from 'react'
import { renderMask } from './_helper'

type Props = {
  annotation: MaskType
  ratio?: number
  simple?: boolean
}

const Mask: FC<Props> = ({ annotation, ratio = 1, simple }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [canvas, setCanvas] = useState<HTMLCanvasElement>()

  useEffect(() => {
    if (canvasRef.current) {
      setCanvas(canvasRef.current)
    }
  }, [canvasRef.current])

  useEffect(() => {
    if (annotation && canvas) {
      renderMask(canvas, annotation, !simple, ratio)
    }
  }, [annotation, canvas])

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'absolute',
        left: 0,
        transformOrigin: 'left top 0',
        transform: `scale(${ratio})`,
      }}
      width={annotation?.width}
      height={annotation?.height}
    ></canvas>
  )
}

export default Mask
