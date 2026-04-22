import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
model = os.environ.get('MODEL', 'gemini-3.1-flash-lite-preview')
prompt = os.environ.get('PROMPT', 'Golden supplement capsules on black background, premium studio shot, no text.')
out = os.environ.get('OUT', '/tmp/gemini_test_output.bin')

resp = client.models.generate_content(
    model=model,
    contents=prompt,
    config=types.GenerateContentConfig(
        response_modalities=['IMAGE','TEXT']
    )
)

print('MODEL', model)
print('HAS_CANDIDATES', bool(getattr(resp, 'candidates', None)))
texts = []
saved = 0
for cand in (resp.candidates or []):
    content = getattr(cand, 'content', None)
    if not content:
        continue
    for part in (content.parts or []):
        if getattr(part, 'text', None):
            texts.append(part.text)
        inline = getattr(part, 'inline_data', None)
        if inline and getattr(inline, 'data', None):
            with open(out, 'wb') as f:
                f.write(inline.data)
            print('SAVED', out, 'MIME', getattr(inline, 'mime_type', None), 'BYTES', len(inline.data))
            saved += 1
print('TEXT', ' | '.join(texts)[:1000])
print('SAVED_COUNT', saved)
