from dotenv import load_dotenv
import os, base64
load_dotenv()

cid = os.environ.get('CLIENT_ID', '')
cs  = os.environ.get('CLIENT_SECRET', '')

print(f'CLIENT_ID    : largo={len(cid)}')
print(f'CLIENT_SECRET: largo={len(cs)}')
print(f'Encoded base64 (primeros 50 chars): {base64.b64encode((cid+":"+cs).encode()).decode()[:50]}...')
