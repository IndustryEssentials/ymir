const llmm = {
  'llmm.tabs.single': { cn: '单张图片验证', en: 'Single Picture Inference' },
  'llmm.tabs.dataset': { cn: '数据集推理', en: 'Dataset Inference' },
  'llmm.prompt.label': { cn: '文本描述', en: 'Text Prompt' },
  'llmm.prompt.placeholder': { cn: '请输入文本描述，将为您生成相应的标注。', en: 'Please input text prompt, for generate responding annotations.' },
  'llmm.prediction.classes.tip': {
    cn: '多模态大模型镜像能够预测模型训练目标之外的类别',
    en: "Multi-modal large-scale models can predict categories beyond the model's training targets",
  },
  'llmm.infer': { cn: '检测', en: 'Detect' },
  'llmm.groundedsam.image.add.tip': { cn: '此功能需要添加Grounded-SAM镜像，是否添加？', en: 'Grounded-SAM image is required, OK to add the image.' },
  'llmm.groundedsam.image.add.success': { cn: 'Grounded-SAM镜像正在导入中，请耐心等待', en: 'Grounded-SAM image is preparing, please wait for done.' },
  'llmm.groundedsam.image.add.user.invalid': {
    cn: 'Grounded-SAM镜像未添加，请联系管理员添加',
    en: 'Grounded-SAM image is required, please contact to administrator to add.',
  },
  'llmm.image.add.tip': {
    en: 'The default image of the LLMM Project is being pulled, you can import data or perform other operations unrelated to the image first',
    cn: '多模态大模型默认镜像正在拉取中，您可以先导入数据或其他不涉及到镜像的操作',
  },
}

export default llmm
