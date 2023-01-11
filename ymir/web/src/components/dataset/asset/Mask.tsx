import { FC, useEffect, useRef, useState } from 'react'
import { renderMask } from './_helper'

type Props = {
  annotation: YModels.Mask
  ratio?: number
  simple?: boolean
}

const Mask: FC<Props> = ({ annotation, ratio = 1 }) => {
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
    if (annotation.decodeMask && canvas) {
      const { decodeMask: mask, color } = annotation
      renderMask(canvas, mask, width, height, color)
    }
  }, [annotation.decodeMask, canvas, width, height])

  useEffect(() => {
    if (!annotation) {
      return
    }
    setRect({
      width: annotation.width,
      height: annotation.height,
    })
  }, [annotation])

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
