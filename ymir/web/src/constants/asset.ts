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

export function transferAsset(data: YModels.BackendData, keywords?: Array<string>): YModels.Asset {
  const { width, height } = data?.metadata || {}
  const colors = generateDatasetColors(keywords || data.keywords)
  const transferAnnotations = (annotations = [], pred = false) =>
    annotations.map((an: YModels.BackendData) => toAnnotation(an, width, height, pred, colors[an.keyword]))

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

export function toAnnotation(annotation: YModels.BackendData, width: number = 0, height: number = 0, pred = false, color = ''): YModels.Annotation {
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

function annotationTransfer(annotation: YModels.BackendData) {
  const type = annotation.type as YModels.AnnotationType
  return {
    [AnnotationType.BoundingBox]: toBoundingBoxAnnoatation,
    [AnnotationType.Polygon]: toPolygonAnnotation,
    [AnnotationType.Mask]: toMaskAnnotation,
  }[type](annotation)
}

export function toBoundingBoxAnnoatation(annotation: YModels.BackendData) {
  const type: YModels.AnnotationType.BoundingBox = annotation.type || AnnotationType.BoundingBox
  return {
    ...annotation,
    box: annotation.box,
    type,
  }
}

export function toMaskAnnotation(annotation: YModels.BackendData) {
  const type: YModels.AnnotationType.Mask = annotation.type || AnnotationType.Mask
  return {
    ...annotation,
    mask: annotation.mask,
    type,
  }
}

export function toPolygonAnnotation(annotation: YModels.BackendData) {
  const type: YModels.AnnotationType.Polygon = annotation.type || AnnotationType.Polygon
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

function getType(annotation: YModels.BackendData) {
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
