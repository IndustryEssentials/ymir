import { Annotation, Asset } from './typings/asset'
import { Backend } from './typings/common'

export enum AnnotationType {
  BoundingBox = 0,
  Polygon = 1,
  Mask = 2,
}

export enum MergeType {
  New = 0,
  Exist = 1,
}

export enum states {
  READY = 0,
  VALID = 1,
  INVALID = 2,
}

export enum evaluationTags {
  tp = 1,
  fp = 2,
  fn = 3,
  mtp = 11,
}

export const evaluationLabel = (tag: evaluationTags) => {
  const maps = {
    [evaluationTags.tp]: 'tp',
    [evaluationTags.fp]: 'fp',
    [evaluationTags.fn]: 'fn',
    [evaluationTags.mtp]: 'mtp',
  }
  return maps[tag]
}

export function transferAsset(data: Backend, keywords?: Array<string>): Asset {
  const { width, height } = data?.metadata || {}
  const colors = generateDatasetColors(keywords || data.keywords)
  const transferAnnotations = (annotations = [], pred = false) => annotations.map((an: Backend) => toAnnotation(an, width, height, pred, colors[an.keyword]))

  const annotations = [...transferAnnotations(data.gt), ...transferAnnotations(data.pred, true)]
  const evaluated = annotations.some((annotation) => evaluationTags[annotation.cm])

  return {
    id: data.id,
    hash: data.hash,
    keywords: data.keywords || [],
    url: data.url,
    type: data.type,
    width,
    height,
    metadata: data.metadata,
    size: data.size,
    annotations,
    evaluated,
    cks: data.cks || {},
  }
}

export function toAnnotation(annotation: Backend, width: number = 0, height: number = 0, pred = false, color = ''): Annotation {
  return {
    id: `${Date.now()}${Math.random()}`,
    keyword: annotation.keyword || '',
    width,
    height,
    cm: annotation.cm,
    gt: !pred,
    tags: annotation.tags || {},
    color,
    ...annotationTransfer({ ...annotation, type: getType(annotation) }),
  }
}

function annotationTransfer(annotation: Backend) {
  const type = annotation.type as AnnotationType
  return {
    [AnnotationType.BoundingBox]: toBoundingBoxAnnoatation,
    [AnnotationType.Polygon]: toPolygonAnnotation,
    [AnnotationType.Mask]: toMaskAnnotation,
  }[type](annotation)
}

export function toBoundingBoxAnnoatation(annotation: Backend) {
  const type: AnnotationType.BoundingBox = annotation.type || AnnotationType.BoundingBox
  return {
    ...annotation,
    box: annotation.box,
    type,
  }
}

export function toMaskAnnotation(annotation: Backend) {
  const type: AnnotationType.Mask = annotation.type || AnnotationType.Mask
  return {
    ...annotation,
    mask: annotation.mask,
    type,
  }
}

export function toPolygonAnnotation(annotation: Backend) {
  const type: AnnotationType.Polygon = annotation.type || AnnotationType.Polygon
  return {
    ...annotation,
    polygon: annotation.polygon,
    type,
  }
}

export function transferAnnotationsCount(count = {}, negative = 0, total = 1) {
  return {
    keywords: Object.keys(count),
    count,
    negative,
    total,
  }
}

function getType(annotation: Backend) {
  return annotation?.mask ? AnnotationType.Mask : annotation?.polygon?.length ? AnnotationType.Polygon : AnnotationType.BoundingBox
}

function generateDatasetColors(keywords: Array<string> = []): {
  [name: string]: string
} {
  const KeywordColor = ['green', 'red', 'cyan', 'blue', 'yellow', 'purple', 'magenta', 'orange', 'gold']
  return keywords.reduce(
    (prev, curr, i) => ({
      ...prev,
      [curr]: KeywordColor[i % KeywordColor.length],
    }),
    {},
  )
}
