import { AnnotationType } from '@/constants/dataset'
import { percent } from '@/utils/number'
import { decode } from '@/utils/rle'

export function mask2Image(mask: number[][], width: number, height: number, color = '') {
  if (!mask) {
    return
  }
  const dataWithColor = mask
    .map((row) => row.map((col) => (col ? [255, 0, 0, 160] : [0, 0, 0, 0])))
    .flat()
    .flat()
  const imageData = Uint8ClampedArray.from(dataWithColor)
  const image = new ImageData(imageData, width, height)
  return image
}

export function renderPolygon(canvas: HTMLCanvasElement, points: YModels.Point[], width: number, height: number) {
  const ctx = canvas.getContext('2d')
  if (!ctx) {
    return
  }
  ctx.beginPath()
  ctx.fillStyle = 'rgba(255, 255, 255, 0.3)'
  ctx.strokeStyle = 'rgba(0, 0, 0, 0.3)'
  ctx.moveTo(points[0].x, points[0].y)
  ctx.lineWidth = 1
  points.forEach((point, index) => index > 0 && ctx.lineTo(point.x, point.y))
  ctx.fill()
}

export function renderMask(canvas: HTMLCanvasElement, mask: number[][], width: number, height: number) {
  const ctx = canvas.getContext('2d')
  if (!ctx) {
    return
  }
  const image = mask2Image(mask, width, height)

  image && ctx.putImageData(image, 0, 0)
}

export function transferAnnotations(annotations: YModels.Annotation[] = [], asset?: YModels.Asset) {
  const handles = (annotation: YModels.Annotation) => {
    switch (annotation.type) {
      case AnnotationType.Polygon:
        return toPolygon(annotation)
      case AnnotationType.Mask:
        return toMask(annotation, asset)
      case AnnotationType.BoundingBox:
      default:
        return toBoundingBox(annotation as YModels.BoundingBox)
    }
  }

  return annotations.map(handles)
}

function toBoundingBox(annotation: YModels.BoundingBox): YModels.BoundingBox {
  return annotation
}

function toMask(annotation: YModels.Mask, asset?: YModels.Asset): YModels.Mask {
  return {
    ...annotation,
    decodeMask: decode(annotation.mask, asset?.height || 0),
  }
}

function toPolygon(annotation: YModels.Polygon): YModels.Polygon {
  return annotation
}
