enum ObjectType {
  ObjectDetection = 2,
  SemanticSegmentation = 3,
  InstanceSegmentation = 4,
}

const typesPrefix = 'project.types.'
const projectTypes = [
  { label: 'det', value: ObjectType.ObjectDetection },
  { label: 'seg', value: ObjectType.SemanticSegmentation },
  { label: 'ins', value: ObjectType.InstanceSegmentation },
]

const getProjectTypes = () => projectTypes.map(({ label, value }) => ({ label: typesPrefix + label, value }))

const getProjectTypeLabel = (type?: ObjectType, prefix: boolean = false) => {
  const target = projectTypes.find(({ value }) => value === type)
  return type ? (prefix ? typesPrefix : '') + target?.label : ''
}

const isDetection = (type?: ObjectType) => type === ObjectType.ObjectDetection

const isSemantic = (type?: ObjectType) => type === ObjectType.SemanticSegmentation

const isInstance = (type?: ObjectType) => type === ObjectType.InstanceSegmentation

export { ObjectType, getProjectTypes, getProjectTypeLabel, isDetection, isSemantic, isInstance }
