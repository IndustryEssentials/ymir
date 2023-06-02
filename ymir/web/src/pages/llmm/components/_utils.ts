import { ImageConfig } from '@/constants'

const transHyperParams = (params: { key: string; value: any }[], prompt: string = '', gpu: number = 1) => {
  const config = params.reduce<ImageConfig>((prev, { key, value }) => ({ ...prev, [key]: value }), {})
  config.text_prompt = prompt.trim()
  config.gpu_count = gpu
  return config
}

export { transHyperParams }
