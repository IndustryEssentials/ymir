import { Card, Modal, ModalProps } from 'antd'
import { FC, useState } from 'react'
import XMLViewer from 'react-xml-viewer'
import JsonViewer from 'react-json-view'
import { ObjectType } from '@/constants/project'

interface Props extends ModalProps {
  objectType: number
}

enum ObjectTypes {
  voc = 'xml',
  coco = 'json',
}

const vocXml = `<annotation>
<folder>VOC_ROOT</folder>                           
<filename>aaaa.jpg</filename>  # filename(required)
<size>                         # image szie（width, height and channel count）                      
  <width>500</width>
  <height>332</height>
  <depth>3</depth>
</size>
<image_quality>1.234</image_quality>       # image quality (optional)
<segmented>1</segmented>       # for segmentation（optional）
<object>                       # object
  <name>horse</name>         # object class
  <pose>Unspecified</pose>   #  shooting angle(optional)
  <truncated>0</truncated>   # truncated
  <difficult>0</difficult>   # recognition degree, 0(easy), 1(difficult) (optional)
  <box_quality>1.234</box_quality>       # box quality 
  <bndbox>                   # bounding-box
    <xmin>100</xmin>
    <ymin>96</ymin>
    <xmax>355</xmax>
    <ymax>324</ymax>
    <rotate_angle>2.889813</rotate_angle>
  </bndbox>
</object>
<object>                       # multiple objects
  <name>person</name>
  <pose>Unspecified</pose>
  <truncated>0</truncated>
  <difficult>0</difficult>
  <box_quality>1.234</box_quality>
  <confidence>0.95</confidence>  # box confidence (for prediction, not VOC standard attribute) (optional)
  <bndbox>
    <xmin>100</xmin>
    <ymin>96</ymin>
    <xmax>355</xmax>
    <ymax>324</ymax>
    <rotate_angle>2.889813</rotate_angle>
  </bndbox>
</object>
</annotation>`

const cocoJson = {
  info: {
    contributor: 'LabelFree',
    date_created: '2022-12-07 07:49:11',
    description: '',
    url: '',
    version: '1.0',
    year: 2022,
  },
  licenses: [],
  images: [
    {
      id: 33,
      width: 2048,
      height: 1024,
      file_name: 'image_name_in_images.png',
    },
  ],
  annotations: [
    {
      id: 30,
      image_id: 33,
      segmentation: [[1191.0962343096237, 314.9121338912134, 1111.8326359832636, '..., polygon format']],
      area: 181829.0,
      bbox: [1071.0, 314.0, 515.0, 438.0],
      iscrowd: 0,
      category_id: 1,
    },
    {
      id: 31,
      image_id: 33,
      segmentation: {
        counts: [23, 34, 34, '..., mask format'],
        size: [1920, 1080],
      },
      area: 41284.0,
      bbox: [494.0, 310.0, 333.0, 166.0],
      iscrowd: 0,
      category_id: 1,
    },
  ],
  categories: [{ name: 'car', supercategory: 'car', id: 1 }],
}

const contents = {
  [ObjectTypes.voc]: <XMLViewer xml={vocXml} />,
  [ObjectTypes.coco]: <JsonViewer src={cocoJson} name={false} />,
}

const FormatDetailModal: FC<Props> = ({ objectType, ...props }) => {
  const isDetection = objectType === ObjectType.ObjectDetection
  const [active, setActive] = useState<ObjectTypes>(isDetection ? ObjectTypes.voc : ObjectTypes.coco)
  const vocTab = { tab: '*.xml', key: ObjectTypes.voc }
  const cocoTab = { tab: 'coco-annotations.json', key: ObjectTypes.coco }
  const tabs = [!isDetection ? cocoTab : vocTab]
  return (
    <Modal width={'80%'} style={{ top: 40 }} {...props} footer={null}>
      <Card tabList={tabs} activeTabKey={active} onTabChange={(value) => setActive(value as ObjectTypes)}>
        {contents[active]}
      </Card>
    </Modal>
  )
}

export default FormatDetailModal
