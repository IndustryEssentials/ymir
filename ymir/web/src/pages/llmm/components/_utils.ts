import { ImageConfig } from '@/constants'

const transHyperParams = (params: { key: string; value: any }[], prompt: string = '', gpu: number = 1) => {
  const config = params.reduce<ImageConfig>((prev, { key, value }) => ({ ...prev, [key]: value }), {})
  config.text_prompt = prompt.trim()
  config.gpu_count = gpu
  return config
}

const classes2Prompt = (classes: string[], preClasses: string[] = []) => {
  const subs = [...new Set([...preClasses, ...classes])].reduce<string[]>((prev, curr) => {
    const target = [...prev, curr]
    return target.join('').length > 256 ? prev : target
  }, [])
  return subs.join(';')
}

export { transHyperParams, classes2Prompt }
