import base64
import os
from typing import Optional, Literal
from datetime import datetime

from openai import OpenAI


class PhotoAgent:
    def __init__(self, model: str = 'gpt-image-1', out_dir: str = 'outputs'):
        self.client = OpenAI()
        self.model = model
        self.out_dir = out_dir
        os.makedirs(self.out_dir, exist_ok=True)

    def generate(
        self,
        prompt: str,

        size: Literal['1024x1024', '1024x1536', '1536x1024', 'auto'] = 'auto',
        quality: Literal['high', 'medium', 'low', 'auto'] = 'auto',
        background: Optional[Literal['transparent']] = None,
        filename: Optional[str] = None,
    ) -> dict:

        resp = self.client.images.generate(
            model=self.model,
            prompt=prompt,
            size=size,
            quality=quality,
            background=background,
        )

        data = resp.data[0]

        url = getattr(data, 'url', None)
        b64 = getattr(data, 'b64_json', None)

        file_path = None
        if b64:
            raw = base64.b64decode(b64)
            if not filename:
                stamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                filename = f'image_{stamp}.png'
            file_path = os.path.join(self.out_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(raw)

        return {
            'prompt': prompt,
            'size': size,
            'url': url,
            'file_path': file_path,
        }


if __name__ == '__main__':
    agent = PhotoAgent(model='gpt-image-1')

    result = agent.generate(
        prompt='Photorealistic Stalin on Parade in Beijing',
        size='1536x1024',
        quality='high',
        # background='transparent',
    )
    print('URL:', result['url'])
    print('FILE:', result['file_path'])