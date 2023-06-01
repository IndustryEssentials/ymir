import { ImageConfig } from '@/constants'

const transHyperParams = (params: { key: string; value: any }[], prompt: string, gpu: number) => {
  const config = params.reduce<ImageConfig>((prev, { key, value }) => ({ ...prev, [key]: value }), {})
  config.text_prompt = prompt
  config.gpu_count = gpu
  return config
}

export { transHyperParams }
