import openaiLogo from '@/assets/providers/openai.svg'
import geminiLogo from '@/assets/providers/gemini.png'
import deepseekLogo from '@/assets/providers/deepseek.png'
import claudeLogo from '@/assets/providers/claude.svg'
import mistralLogo from '@/assets/providers/mistral.png'

export const PROVIDERS = [
    { id: 1, provider: 'openai',    label: 'OpenAI',    client: 'openai',    url: null,                            image: openaiLogo },
    { id: 2, provider: 'gemini',    label: 'Gemini',    client: 'gemini',    url: null,                            image: geminiLogo },
    { id: 3, provider: 'anthropic', label: 'Claude',    client: 'anthropic', url: null,                            image: claudeLogo },
    { id: 4, provider: 'deepseek',  label: 'DeepSeek',  client: 'openai',    url: 'https://api.deepseek.com/v1',   image: deepseekLogo },
    { id: 5, provider: 'mistral',   label: 'Mistral',   client: 'mistral',   url: null,                            image: mistralLogo },
]
