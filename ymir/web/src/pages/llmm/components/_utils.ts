import { ImageConfig } from '@/constants'

const transHyperParams = (params: { key: string; value: any }[], prompt: string) => {
  const config = params.reduce<ImageConfig>((prev, { key, value }) => ({ ...prev, [key]: value }), {})
  config.text_prompt = prompt
  return config
}

export { transHyperParams }
