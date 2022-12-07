import { FC, useEffect, useRef, useState } from 'react'
import { renderMask } from './_helper'
type Props = {
  annotation: YModels.Mask
  ratio?: number
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
      const { decodeMask: mask } = annotation
      renderMask(canvas, mask, width, height)
    }
  }, [annotation.decodeMask, canvas, width, height])

  useEffect(() => {
    if (!annotation) {
      return
    }
    setRect({
      width: annotation.width * ratio,
      height: annotation.height * ratio,
    })
  }, [ratio, annotation])

  return (
    <canvas
      ref={canvasRef}
      style={{
        transform: `translate(50%, 50%) scale(${ratio})`,
      }}
      width={width}
      height={height}
    ></canvas>
  )
}

export default Mask
