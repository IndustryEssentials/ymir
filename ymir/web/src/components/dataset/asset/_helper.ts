export function mask2Image (mask: number[][], width: number, height: number, color = '') {
  if (!mask) {
    return
  }
  const dataWithColor = mask.map(row => row.map(col => col ? [255, 0, 0, 160] : [0, 0, 0, 0])).flat().flat()
    const imageData = Uint8ClampedArray.from(dataWithColor)
    const image = new ImageData(imageData, width, height)
    return image
}

export function renderPolygon(canvas: HTMLCanvasElement, points: YModels.Point[], width: number, height: number) {
  const ctx = canvas.getContext('2d')
  if (!ctx) {
    return
  }
  canvas.width = width
  canvas.height = height
  ctx.beginPath()
  ctx.moveTo(points[0].x, points[0].y)
  points.forEach((point, index) => index > 0 && ctx.lineTo(point.x, point.y))
  ctx.fill()
}

export function renderMask (canvas: HTMLCanvasElement, mask: number[][], width: number, height: number) {  
  const ctx = canvas.getContext('2d')
  if (!ctx) {
    return
  }
  canvas.width = width
  canvas.height = height
  const image = mask2Image(mask,width, height)

  image && ctx.putImageData(image, 0, 0)
}