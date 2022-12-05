import { FC, useEffect, useRef, useState } from 'react'
import { renderMask } from './_helper'
type Props = {
  annotation: YModels.Mask
}

const Mask: FC<Props> = ({ annotation }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [canvas, setCanvas] = useState<HTMLCanvasElement>()
  useEffect(() => {
    if (canvasRef.current) {
      setCanvas(canvasRef.current)
    }
  }, [canvasRef.current])

  useEffect(() => {
    if (annotation.decodeMask && canvas) {
      const { decodeMask: mask, width, height } = annotation
      renderMask(canvas, mask, width, height)
    }
  }, [annotation.decodeMask, canvas])

  return <canvas ref={canvasRef}></canvas>
}

export default Mask
