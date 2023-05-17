enum ObjectType {
  ObjectDetection = 2,
  SemanticSegmentation = 3,
  InstanceSegmentation = 4,
  MultiModal = 50,
}

const typesPrefix = 'project.types.'
const projectTypes = [
  { label: 'det', value: ObjectType.ObjectDetection },
  { label: 'seg', value: ObjectType.SemanticSegmentation },
  { label: 'ins', value: ObjectType.InstanceSegmentation },
  { label: 'mul', value: ObjectType.MultiModal },
]

const getProjectTypes = () => projectTypes.map(({ label, value }) => ({ label: typesPrefix + label, value }))

const getProjectTypeLabel = (type?: ObjectType, prefix: boolean = false) => {
  const target = projectTypes.find(({ value }) => value === type)
  return type ? (prefix ? typesPrefix : '') + target?.label : ''
}

const isDetection = (type?: ObjectType) => type === ObjectType.ObjectDetection

const isSemantic = (type?: ObjectType) => type === ObjectType.SemanticSegmentation

const isInstance = (type?: ObjectType) => type === ObjectType.InstanceSegmentation

const isSegmentation = (type: ObjectType) => [ObjectType.InstanceSegmentation, ObjectType.SemanticSegmentation].includes(type)

const isMultiModal = (type?: ObjectType) => type === ObjectType.MultiModal

export { ObjectType, getProjectTypes, getProjectTypeLabel, isDetection, isSemantic, isInstance, isMultiModal, isSegmentation }
