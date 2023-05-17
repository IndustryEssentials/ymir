import { AnnotationType } from '../asset'
import { ObjectType } from '../objectType'
import { Classes, CustomClass } from './class'
import { Matable } from './common'

interface Asset {
  id: number
  hash: string
  keywords: Classes
  url: string
  type: ObjectType
  width: number
  height: number
  metadata?: {
    width: number
    height: number
    image_channels?: number
    timestamp: {
      start: string
      duration?: number
    }
  }
  size?: number
  annotations: Annotation[]
  evaluated?: boolean
  cks?: CustomClass
}

interface AnnotationBase {
  id: string | number
  keyword: string
  width: number
  height: number
  color?: string
  score?: number
  gt?: boolean
  cm: number
  tags?: CustomClass
}

type AnnotationMaps = {
  [AnnotationType.BoundingBox]: BoundingBox
  [AnnotationType.Polygon]: Polygon
  [AnnotationType.Mask]: Mask
}

type Point = {
  x: number
  y: number
}

type Annotation = Matable<AnnotationMaps>

type SegAnnotation = Matable<Omit<AnnotationMaps, AnnotationType.BoundingBox>>
type DetAnnotation = Matable<Pick<AnnotationMaps, AnnotationType.BoundingBox>>

interface BoundingBox extends AnnotationBase {
  type: AnnotationType.BoundingBox
  box: {
    x: number
    y: number
    w: number
    h: number
    rotate_angle?: number
  }
}

interface Polygon extends AnnotationBase {
  type: AnnotationType.Polygon
  polygon: Point[]
}

interface Mask extends AnnotationBase {
  type: AnnotationType.Mask
  mask: string
  decodeMask?: number[][]
  rect?: [x: number, y: number, width: number, height: number]
}

export { Asset, AnnotationBase, Annotation, SegAnnotation, DetAnnotation, BoundingBox, Polygon, Mask }
