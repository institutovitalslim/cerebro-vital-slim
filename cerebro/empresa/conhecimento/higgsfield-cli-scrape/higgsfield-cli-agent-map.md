# Mapa Higgsfield CLI para agentes IVS / Content OS

- **Gerado em:** 2026-06-25T18:31:28.284859+00:00
- **Escopo:** CLI Higgsfield público/autenticado em modo leitura, sem geração de mídia.
- **Fontes:** README/MODELS GitHub + `higgsfield --help` + `model list/get --json` + listas Marketing Studio.

## Guardrails IVS

- Não usar Higgsfield para publicar automaticamente. A saída é asset/URL para revisão.
- Não usar rosto/pessoa real sem autorização e fonte de imagem aprovada.
- Conteúdo clínico/promessa/resultado passa por compliance Content OS e Ana quando necessário.
- Não inserir PII, conversa de paciente, prontuário ou lead individual em prompt.
- Para geração real, checar créditos com `higgsfield account status` e preferir `--wait` para entregar URL final.

## Inventário vivo

| Métrica | Valor |
|---|---:|
| Modelos totais | 78 |
| Modelos tipo `3d` | 5 |
| Modelos tipo `audio` | 4 |
| Modelos tipo `image` | 36 |
| Modelos tipo `text` | 1 |
| Modelos tipo `video` | 32 |
| Hooks Marketing Studio | 9 |
| Settings Marketing Studio | 14 |
| Ad formats DTC | 42 |

## Matriz de uso rápido — intenção → comando

| Intenção | Padrão | Comando base | Uso no Content OS |
|---|---|---|---|
| Imagem premium geral, carrossel, banner, texto em imagem, design limpo | `gpt_image_2` | `higgsfield generate create gpt_image_2 --prompt "..." --aspect_ratio 4:5 --quality high --resolution 2k --wait` | Criativos estáticos, thumbnails, capas de carrossel, variações visuais com texto curto. |
| Imagem com personagem/referência/estilo consistente | `nano_banana_2 ou nano_banana_flash` | `higgsfield generate create nano_banana_2 --prompt "..." --image ./ref.png --aspect_ratio 9:16 --wait` | Mascotes, personagens recorrentes, avatar visual de campanha. |
| Retrato/identidade consistente treinada | `text2image_soul_v2` | `higgsfield generate create text2image_soul_v2 --prompt "..." --soul-id <soul_id> --quality 2k --wait` | Só usar com identidade autorizada; útil para apresentadores/brand persona. |
| Ambiente/local/cenário sem pessoas | `cinematic_studio_soul_location` | `higgsfield generate create cinematic_studio_soul_location --prompt "clínica premium, luz natural..." --aspect_ratio 16:9 --wait` | Bastidores sintéticos, cenários premium, ambientações de campanha. |
| Vídeo vertical/reel cinematográfico sério | `seedance_2_0` | `higgsfield generate create seedance_2_0 --prompt "..." --aspect_ratio 9:16 --duration 5 --resolution 1080p --wait --wait-timeout 20m` | Reels de autoridade, transições, vídeos curtos de conceito. |
| Image-to-video a partir de frame aprovado | `seedance_2_0` | `higgsfield generate create seedance_2_0 --prompt "camera push-in..." --start-image ./frame.png --aspect_ratio 9:16 --duration 5 --wait` | Animar capa/arte aprovada no Content OS. |
| Vídeo simples, plano único, custo menor | `kling3_0` | `higgsfield generate create kling3_0 --prompt "..." --start-image ./frame.png --duration 5 --mode pro --wait` | Teste rápido quando Seedance for excesso. |
| UGC/ad com avatar + produto + hook/setting | `marketing_studio_video` | `higgsfield generate create marketing_studio_video --prompt "..." --avatars @avatars.json --product_ids @products.json --mode ugc --duration 15 --aspect_ratio 9:16 --resolution 720p --wait --wait-timeout 30m` | Anúncios UGC, demonstração, product review. Usar hook/setting só nos modos compatíveis. |
| Imagem publicitária com layout/headline/benefícios | `marketing_studio_image / dtc-ads` | `higgsfield marketing-studio dtc-ads generate --prompt "..." --format-id <id> --wait` | Stack de anúncios estáticos e variações de promessa/benefício. |
| Importar produto por URL para Marketing Studio | `products fetch` | `higgsfield marketing-studio products fetch --url https://... --wait` | Criar entidade reutilizável de produto/oferta antes de gerar ads. |
| Product photoshoot/hero de produto | `product-photoshoot` | `higgsfield product-photoshoot create --mode lifestyle_scene --prompt "..." --image ./produto.png --count 3 --wait` | Fotos premium de produto/kit/serviço visual, quando houver imagem base. |
| Marketplace cards / imagens secundárias | `marketplace-cards` | `higgsfield marketplace-cards create --scope product-images --prompt "..." --image ./produto.png --wait` | Cards de oferta, módulos A+, imagens de landing/comercial. |
| Analisar viralidade de vídeo pronto | `brain_activity` | `higgsfield generate create brain_activity --video ./reel.mp4 --wait` | Gate pós-produção: hook, atenção, retenção e pontos fracos antes de publicar. |
| Upload explícito de mídia | `upload create` | `higgsfield upload create ./arquivo.png --json` | Opcional; generate create auto-uploada caminhos locais. |

## Modelos prioritários para o IVS

| Modelo | Tipo | Quando usar | Parâmetros principais |
|---|---|---|---|
| `gpt_image_2` — GPT Image 2 | image | imagem premium geral, banners, capa, texto em imagem, carrossel | `--aspect-ratio` ['1:1', '4:3', '3:4', '16:9', '9:16', '3:2', '2:3'], `--batch-size` default=1, `media flags`, `--prompt`*, `--quality` ['low', 'medium', 'high'], `--resolution` ['1k', '2k', '4k'] |
| `nano_banana_2` — Nano Banana Pro | image | personagem/referência/edição criativa difícil | `--aspect-ratio` ['auto', '1:1', '3:2', '2:3', '4:3', '3:4', '4:5', '5:4', '9:16', '16:9', '21:9'], `--folder-id`, `--input-images`, `--prompt`*, `--resolution` ['1k', '2k', '4k'] |
| `nano_banana_flash` — Nano Banana 2 | image | iteração mais rápida de personagem/referência | `--aspect-ratio` ['1:1', '3:2', '2:3', '4:3', '3:4', '4:5', '5:4', '9:16', '16:9', '21:9'], `media flags`, `--prompt`*, `--resolution` ['1k', '2k', '4k'] |
| `flux_2` — FLUX.2 | image | imagem geral alternativa/experimentos visuais | `--aspect-ratio` ['1:1', '4:3', '3:4', '16:9', '9:16'], `--input-images`, `--model` ['pro', 'flex', 'max'], `--prompt`*, `--resolution` ['1k', '2k'] |
| `text2image_soul_v2` — Higgsfield Soul V2 | image | identidade/rosto treinado autorizado | `--aspect-ratio` ['1:1', '16:9', '9:16', '4:3', '3:4', '3:2', '2:3'], `--custom-reference-id`, `media flags`, `--prompt`*, `--quality` ['1.5k', '2k'] |
| `cinematic_studio_soul_location` — Cinematic Studio Soul Location | image | locações e cenários premium | `--aspect-ratio` ['1:1', '16:9', '9:16', '4:3', '3:4', '3:2', '2:3', '21:9', '9:21'], `--prompt`* |
| `cinematic_studio_soul_cast` — Cinematic Studio Soul Cast | image | personas/personagens cinematográficos | `--aspect-ratio` ['1:1', '16:9', '9:16', '4:3', '3:4', '3:2', '2:3', '5:4', '4:5', '21:9', '9:21'], `--budget` default=50, `--prompt` |
| `seedance_2_0` — Seedance 2.0 | video | vídeo principal/reels/image-to-video | `--aspect-ratio` ['auto', '16:9', '9:16', '4:3', '3:4', '1:1', '21:9'], `--bitrate-mode` ['standard', 'high'], `--duration` default=5, `--generate-audio` default=True, `--genre` ['auto', 'action', 'horror', 'comedy', 'noir', 'drama', 'epic'], `media flags`, `--mode` ['std', 'fast'], `--prompt`*, `--resolution` ['480p', '720p', '1080p', '4k'] |
| `kling3_0` — Kling v3.0 | video | vídeo plano único/alternativa econômica | `--aspect-ratio` ['16:9', '9:16', '1:1'], `--duration` default=5, `media flags`, `--mode` ['pro', 'std', '4k'], `--prompt`*, `--sound` ['on', 'off'] |
| `veo3_1` — Google Veo 3.1 | video | vídeo alternativo/volume quando disponível | `--aspect-ratio` ['16:9', '9:16'], `--duration` ['4', '6', '8'], `--input-image`, `--model` ['veo-3-1-preview', 'veo-3-1-fast'], `--prompt`*, `--quality` ['basic', 'high', 'ultra'] |
| `marketing_studio_video` — Marketing Studio Video | video | UGC e anúncios com avatar/produto | `--ad-reference-id`, `--aspect-ratio` ['auto', '21:9', '16:9', '4:3', '1:1', '3:4', '9:16'], `--avatar-ids`, `--avatars`, `--duration` default=15, `--generate-audio` default=False, `--hook-id`, `media flags`, `--mode` default=ugc, `--product-ids`, `--prompt`*, `--resolution` ['480p', '720p', '1080p'], `--setting-id`, `--web-product-ids` |
| `marketing_studio_image` — Marketing Studio Image | image | imagem publicitária Marketing Studio | `--aspect-ratio` ['auto', '1:1', '3:2', '2:3', '4:3', '3:4', '4:5', '5:4', '9:16', '16:9', '21:9'], `--input-images`, `--prompt`*, `--resolution` ['1k', '2k', '4k'] |
| `brain_activity` — Brain Activity | text | Virality Predictor para vídeo pronto | `--folder-id`, `media flags`* |
| `text2speech_v2` — text2speech_v2 | audio | voz/TTS quando necessário | `--model`* ['elevenlabs', 'minimax', 'seed_speech', 'vibe_voice', 'cozy_voice'], `--prompt`*, `--voice-id`*, `--voice-type`* ['preset', 'element'] |

## Marketing Studio — playbook

### Discovery
```bash
higgsfield marketing-studio avatars list --json
higgsfield marketing-studio products list --json
higgsfield marketing-studio hooks list --json
higgsfield marketing-studio settings list --json
higgsfield marketing-studio ad-formats list --json
```

### Produto por URL
```bash
higgsfield marketing-studio products fetch --url https://exemplo.com/produto --wait
```

### Vídeo UGC com produto/avatar
```bash
printf '["<product_id>"]' > products.json
printf '[{"id":"<avatar_id>","type":"preset"}]' > avatars.json
higgsfield generate create marketing_studio_video \
  --prompt "UGC vertical, abertura forte, benefício claro, CTA suave" \
  --avatars @avatars.json \
  --product_ids @products.json \
  --mode ugc \
  --duration 15 \
  --aspect_ratio 9:16 \
  --resolution 720p \
  --wait --wait-timeout 30m
```

### DTC Ads Engine — imagem com formato obrigatório
```bash
higgsfield marketing-studio ad-formats list --json
higgsfield marketing-studio dtc-ads generate \
  --prompt "headline curta, benefício visual, prova/autoridade, estética premium IVS" \
  --format-id <format_id> \
  --wait
```

### Hooks disponíveis — nomes

- `3d45fb46-254f-4c83-9685-8e3d28945a67` — **Product Hit** (stunt): Object flies into frame, hits subject. Brief reaction → pivot to product.
- `75b6d501-be0e-4416-a7ed-52f04f180574` — **Spicy** (subtle): The shot starts with an extreme close-up of a collarbone, slowly tilts up to reveal a flawless makeup look, then pulls back into selfie framing before a silent pause leads into the product pitch.
- `26cac2dd-99cb-4818-a678-509b0dab2c32` — **Interview** (subtle): Interviewer asks a second stranger a question based entirely on the first stranger's random answer; confusion builds until the second person naturally notices the product (Erewhon-style aspirational item) and pivots into
- `d50eb41c-fcfa-4f4d-93aa-473cdc6bc3b2` — **Random Object Mic** (stunt): During a casual vlog, a random absurd object falls into the person's hand from above, and they immediately use it as a microphone to continue a completely serious product review.
- `8101cd3e-3cc9-4607-a171-3582daa2f6ee` — **Product Crash** (subtle): The product itself falls from above and destroyed, creating chaos; harsh sharpness leads to a perfectly clean and restored scene where a person calmly begins reviewing the product.
- `31976cc7-e597-4be2-9753-4a80153b0cc7` — **Blizzard** (stunt): A cozy indoor scene is suddenly hit by a violent, impossible blizzard; chaos fills the room but the product remains intact and functioning, and once the storm stops, the product is still working.
- `2db84ed8-7082-4981-9c9c-9d61b3c28668` — **Camera Bump** (subtle): The camera operator accidentally bumps into a person, hitting their forehead; they react briefly, recover, and naturally reveal the dress (or product on it) while transitioning into a casual explanation.
- `5443eff1-d940-4ad3-9413-957bb048a6b0` — **Product Dodge** (stunt): Suddenly, a product flies into a person's face; he quickly bends down to avoid a collision, and in the next frame he stands up straight and already holds the product in his hands and begins to review as if nothing had ha
- `ec9fdf99-314d-480d-a656-10d9861341e7` — **Epic Fail** (subtle): A person performs an unsuccessful backflip, lands unsuccessfully, falls, and immediately, without pause, takes out the product and begins an unflappable review.

### Settings disponíveis — nomes

- `b8368076-35eb-4045-b33b-74b2646d9863` — **Bedroom** (realistic): On bed or propped against pillows, soft window light. Unmade bed, cozy textures. Relaxed morning or evening wind-down vibe — honest, low-effort feel.
- `b03705e5-bbed-4d83-8d29-3bc2101cd14f` — **Airplane Wing** (unrealistic): Person sits on airplane wing mid-flight at altitude. Casual product review — powerful wind, clouds, engine roar.
- `10f47b85-abd7-4899-b6b6-91ff2969d3bf` — **Nature** (realistic): Outdoors — trail, park, beach, or garden depending on product. Natural light, greenery or open sky. Active or peaceful mood — setting adapts to product.
- `3cf2164e-ffac-4867-9c43-1d673a5cb28a` — **Roofing** (unrealistic): Person on the edge of a skyscraper rooftop, city skyline stretched out behind, wind moving through hair, sun catching the buildings. Casual product review with the entire city below, character completely unbothered by th
- `6bfbe372-e50a-4900-adee-d4cbd0db8a2f` — **Gym** (realistic): Gym floor, locker room, or post-workout bench. Bright overhead lighting, equipment in background. Sweaty or freshly finished energy — product tied to performance or recovery.
- `e99c2ee8-3c4a-4697-9a58-908e73c9ad38` — **Volcano Rim** (unrealistic): Person sits on active volcano rim, lava below. Casual product review — lava bubbles, smoke drifts through, zero reaction.
- `189fa1ac-1fdc-44f4-bdea-8804a76f0659` — **Bathroom** (realistic): Mirror selfie or front camera in bathroom. Ring light or vanity lighting, tiles visible. Intimate getting-ready energy — product shown mid-routine, close-up friendly.
- `f495493f-0251-4bd7-afc0-90bc6a862e04` — **Tiny Reviewer** (unrealistic): Person shrunk to 15cm next to a product their full height. Normal selfie review at impossible scale — leans on it.
- `a0eb0be9-f0ff-4aee-9dee-69d9fd20110a` — **Kitchen** (realistic): Standing at counter or leaning on island, natural daylight. Clean surface, mug or fruit in background. Casual mid-day energy — product fits daily routine.
- `d6992aea-4521-4606-9e4f-8c766e12622c` — **Car Roof** (unrealistic): Person on roof of moving car, desert highway, golden hour. Product review while swaying with the road. Semi truck passes — no flinch.
- `fdfa032c-801f-4602-8dfd-1162b0f8c9c9` — **In Car** (realistic): Selfie from passenger or driver seat, parked or cruising. Window light on face. Casual tone — talking to camera between errands.
- `8c95f9ba-5849-44b1-82d0-9f6b33240758` — **Street** (realistic): Walking on sidewalk or standing on urban street, handheld selfie. City backdrop — storefronts, traffic, pedestrians. Energetic pace, talking while moving. Spontaneous discovery feel.
- `d39dda10-643c-44e2-bfc8-2451dddde7d9` — **Office** (realistic): Desk setup, laptop open, coffee nearby. Clean modern space, soft overhead or monitor glow. Hushed mid-workday tone — quick product mention squeezed between tasks.
- `71f61bb0-dfd9-459b-a220-0dd468b977d5` — **Train Surf** (unrealistic): Person hangs outside a moving train, filming selfie.  Reviews product — wind pressing on them is the live demo.

## Catálogo completo por tipo

### 3d

| job_set_type | Nome | Required | Opcionais/Enums principais |
|---|---|---|---|
| `3d_rigging` | 3D Rigging | model_url | animation_action_id, enable_animation=False, enable_safety_checker, folder_id, height_meters, model_url |
| `image_to_3d` | Image to 3D | medias | animation_action_id, enable_animation=False, enable_pbr, enable_rigging=False, enable_safety_checker, folder_id, pose_mode, rigging_height_meters, seed, should_remesh, should_texture=False, symmetry_mode, target_polycount, texture_image_url, texture_prompt, topology |
| `multi_image_to_3d` | Multi-Image to 3D | medias | animation_action_id, enable_animation=False, enable_pbr, enable_rigging=False, enable_safety_checker, folder_id, pose_mode, rigging_height_meters, seed, should_remesh, should_texture=False, symmetry_mode, target_polycount, texture_image_url, texture_prompt, topology |
| `sam_3_3d` | 3D Objects | medias | detection_threshold, export_textured_glb=True, folder_id, prompt=, seed |
| `tripo_3d` | Text to 3D | prompt | auto_size=False, face_limit, folder_id, geometry_quality=standard/detailed, negative_prompt, pbr=True, prompt, seed, texture=True, texture_quality=standard/detailed |

### audio

| job_set_type | Nome | Required | Opcionais/Enums principais |
|---|---|---|---|
| `inworld_text_to_speech` | Inworld Text to Speech | prompt, voice | prompt, voice |
| `mirelo_text_to_audio` | Mirelo Text to Audio | duration, prompt | duration, prompt |
| `sonilo_music` | Sonilo Music | duration, prompt | duration, prompt |
| `text2speech_v2` | text2speech_v2 | model, prompt, voice_id, voice_type | model=elevenlabs/minimax/seed_speech/vibe_voice/cozy_voice, prompt, voice_id, voice_type=preset/element |

### image

| job_set_type | Nome | Required | Opcionais/Enums principais |
|---|---|---|---|
| `autosprite` | AutoSprite Animation | image_url | folder_id, frame_count=25, frame_size=256, image_url, is_humanoid=True, kind=idle/walk/run/attack/jump/custom/iso_idle_up/iso_idle_northeast, name, prompt, remove_bg=default/ultra, video_tier=turbo/pro/max, with_sound=False |
| `bytedance_image_upscale` | Bytedance Image Upscale | medias | folder_id, resolution=2k/4k |
| `cinematic_studio_2_5` | Cinematic Studio 2.5 | prompt | aspect_ratio=1:1/4:3/3:4/16:9/9:16, prompt, resolution=1k/2k/4k |
| `cinematic_studio_image` | Cinematic Studio Image | camera_focal_length_id, camera_lens_id, camera_model_id, prompt | aspect_ratio=1:1/4:3/3:4/16:9/9:16/3:2/2:3/21:9, batch_size=1, camera_aperture_id, camera_focal_length_id, camera_lens_id, camera_model_id, prompt, resolution=1k/2k/4k |
| `cinematic_studio_soul_cast` | Cinematic Studio Soul Cast | - | aspect_ratio=1:1/16:9/9:16/4:3/3:4/3:2/2:3/5:4, budget=50, prompt |
| `cinematic_studio_soul_location` | Cinematic Studio Soul Location | prompt | aspect_ratio=1:1/16:9/9:16/4:3/3:4/3:2/2:3/21:9, prompt |
| `color_grading_lut` | Color Grading LUT | medias | folder_id |
| `flux_2` | FLUX.2 | prompt | aspect_ratio=1:1/4:3/3:4/16:9/9:16, input_images, model=pro/flex/max, prompt, resolution=1k/2k |
| `flux_kontext` | Flux Kontext | prompt | aspect_ratio=1:1/4:3/3:4/16:9/9:16, input_images, prompt |
| `gpt_image_2` | GPT Image 2 | prompt | aspect_ratio=1:1/4:3/3:4/16:9/9:16/3:2/2:3, batch_size=1, prompt, quality=low/medium/high, resolution=1k/2k/4k |
| `grok_image` | Grok Image | prompt | aspect_ratio=1:1/4:3/3:4/16:9/9:16, mode=std/quality, prompt |
| `image_auto` | Image Auto | prompt | aspect_ratio=1:1/4:3/3:4/16:9/9:16, prompt |
| `image_background_remover` | Image Background Remover | medias |  |
| `image_decompose` | Image Decompose | medias | folder_id, mode=granular/standard |
| `kling_omni_image` | Kling O1 Image | prompt | aspect_ratio=1:1/auto/16:9/9:16/4:3/3:4/3:2/2:3, input_images, prompt, resolution=1k/2k |
| `marketing_studio_image` | Marketing Studio Image | prompt | aspect_ratio=auto/1:1/3:2/2:3/4:3/3:4/4:5/5:4, input_images, prompt, resolution=1k/2k/4k |
| `ms_image` | MS Image | prompt | aspect_ratio=auto/1:1/3:2/2:3/4:3/3:4/4:5/5:4, avatars, batch_size=1, brand_kit_id, folder_id, product_ids, prompt, quality=low/medium/high, resolution=1k, style_id |
| `nano_banana` | Nano Banana | prompt | aspect_ratio=auto/1:1/3:2/2:3/4:3/3:4/4:5/5:4, input_images, prompt |
| `nano_banana_2` | Nano Banana Pro | prompt | aspect_ratio=auto/1:1/3:2/2:3/4:3/3:4/4:5/5:4, folder_id, input_images, prompt, resolution=1k/2k/4k |
| `nano_banana_2_ai_stylist` | Nano Banana Pro | input_image | background_preset_id, folder_id, input_image, outfit_preset_ids, pose_preset_id, user_outfit_ids |
| `nano_banana_2_shots` | Nano Banana Pro | input_images | aspect_ratio=auto/1:1/3:2/2:3/4:3/3:4/4:5/5:4, folder_id, input_images |
| `nano_banana_2_skin_enhancer` | Nano Banana Pro | input_image, preset_id | folder_id, input_image, preset_id |
| `nano_banana_flash` | Nano Banana 2 | prompt | aspect_ratio=1:1/3:2/2:3/4:3/3:4/4:5/5:4/9:16, prompt, resolution=1k/2k/4k |
| `openai_hazel` | OpenAI Hazel | prompt | aspect_ratio=1:1/3:2/2:3/auto, input_images, prompt, quality=low/medium/high |
| `outpaint` | Outpaint | medias | aspect_ratio=auto/1:1/3:2/2:3/4:3/3:4/4:5/5:4, folder_id |
| `recraft_v4_1` | Recraft V4.1 | prompt | aspect_ratio=1:1/3:4/4:3/4:5/5:4/3:2/2:3/16:9, background_color, batch_size=1, colors, model_type=standard/vector/utility/utility_vector, prompt, resolution=1k/2k |
| `seedream_v4_5` | Seedream 4.5 | prompt | aspect_ratio=1:1/4:3/16:9/3:2/21:9/3:4/9:16/2:3, input_images, prompt, quality=basic/high |
| `seedream_v5_lite` | Seedream V5 Lite | prompt | aspect_ratio=1:1/4:3/3:4/16:9/9:16, prompt, quality=basic/high |
| `soul_cast` | Soul Cast | - | aspect_ratio=1:1/16:9/9:16/4:3/3:4/3:2/2:3/5:4, budget=50, prompt |
| `soul_cinema_studio` | soul_cinema_studio | prompt | aspect_ratio=1:1/16:9/9:16/4:3/3:4/3:2/2:3/21:9, custom_reference_id, enhance_prompt=False, prompt, quality=1.5k/2k, style_id |
| `soul_cinematic` | Soul Cinematic | prompt | aspect_ratio=1:1/16:9/9:16/4:3/3:4/3:2/2:3/21:9, custom_reference_id, prompt, quality=1.5k/2k |
| `soul_location` | Soul Location | prompt | aspect_ratio=1:1/16:9/9:16/4:3/3:4/3:2/2:3/21:9, prompt |
| `text2image_soul_v2` | Higgsfield Soul V2 | prompt | aspect_ratio=1:1/16:9/9:16/4:3/3:4/3:2/2:3, custom_reference_id, prompt, quality=1.5k/2k |
| `topaz_image` | Topaz | input_image, output_height, output_width | denoise=0, face_enhancement=False, face_enhancement_creativity=0, face_enhancement_strength=0, folder_id, input_image, model=Standard V2/Low Resolution V2/CGI/High Fidelity V2/Text Refine, output_height, output_width, sharpen=0 |
| `topaz_image_generative` | Topaz | input_image, output_height, output_width | autoprompt=True, creativity=1, denoise=0, face_enhancement=False, face_enhancement_creativity=0, face_enhancement_strength=0, folder_id, input_image, model=Standard MAX/Redefine/Recovery/Recovery V2, output_height, output_width, prompt=, sharpen=0, texture=1 |
| `z_image` | Z Image | prompt | aspect_ratio=1:1/4:3/3:4/16:9/9:16, prompt |

### text

| job_set_type | Nome | Required | Opcionais/Enums principais |
|---|---|---|---|
| `brain_activity` | Brain Activity | medias | folder_id |

### video

| job_set_type | Nome | Required | Opcionais/Enums principais |
|---|---|---|---|
| `bytedance_video_upscale` | Bytedance Video Upscale | - | duration, folder_id, fps=24, model_version=standard/pro, preset=common/aigc/short_series/ugc/old_film, resolution=1080p/2k/4k |
| `cinematic_studio_3_0` | Cinematic Studio 3.0 | prompt | aspect_ratio=16:9/9:16/1:1, duration=5, generate_audio=False, prompt |
| `cinematic_studio_video` | Cinematic Studio Video | prompt | aspect_ratio=1:1/4:3/3:4/16:9/9:16, duration=5/10, prompt, slow_motion=False, sound=True |
| `cinematic_studio_video_3_5` | Cinematic Studio Video 3.5 | - | aspect_ratio=auto/21:9/16:9/4:3/1:1/3:4/9:16, batch_size=1, camera_aperture_id, camera_focal_length_id, camera_lens_id, camera_model_id, camera_style, color_grading, duration=15, enhance_prompt=False, folder_id, generate_audio=False, genre=auto/action/horror/comedy/noir/drama/epic, light_scheme, multi_prompt, multi_shot_mode=auto/custom, multi_shots=False, prompt=, prompt_language=en/zh, resolution=480p/720p/1080p, style_id, style_prompt |
| `cinematic_studio_video_v2` | Cinematic Studio Video V2 | prompt | aspect_ratio=1:1/4:3/3:4/16:9/9:16, duration=5, genre=auto/action/horror/comedy/western/suspense/intimate/spectacle, mode=pro/std, prompt, sound=on/off |
| `clipify` | Clipify | urls | clip_aspect=9:16/1:1/16:9, clips_num=10, folder_id, max_height=1080, segment_seconds=10, subtitle_case=lower/upper/as-is, subtitle_font=notosans, subtitle_highlight_hex=#FFE84D, subtitle_position=bottom/center/top, track_face_crop=True, urls |
| `draw_to_video` | Draw To Video | prompt, sketch, video | aspect_ratio=auto/21:9/16:9/4:3/1:1/3:4/9:16, duration, enhancer=True, folder_id, generate_audio=False, prompt, ref_image, resolution=480p/720p/1080p, sketch, video |
| `dubbing` | dubbing | input_video, target_language | folder_id, input_video, target_language=eng/cmn/fra/hin/ita/jpn/kor/por |
| `grok_video` | Grok Video | prompt | aspect_ratio=16:9/9:16/1:1, duration=5, prompt |
| `grok_video_v15` | Grok Video 1.5 | medias, prompt | duration=5, prompt, resolution=480p/720p |
| `kling2_6` | Kling 2.6 Video | prompt | aspect_ratio=16:9/9:16/1:1, duration=5/10, input_image, prompt, sound=True |
| `kling3_0` | Kling v3.0 | prompt | aspect_ratio=16:9/9:16/1:1, duration=5, mode=pro/std/4k, prompt, sound=on/off |
| `kling3_0_motion_control` | Kling 3.0 Motion Control | medias | background_source=input_image/input_video, folder_id, mode=std/pro |
| `kling3_0_turbo` | Kling 3.0 Turbo | prompt | aspect_ratio=16:9/9:16/1:1, duration=5, prompt, resolution=720p/1080p |
| `llm_text` | LLM Generation | model | input_images, model, reasoning_effort, system_prompt=, user_prompt= |
| `marketing_studio_video` | Marketing Studio Video | prompt | ad_reference_id, aspect_ratio=auto/21:9/16:9/4:3/1:1/3:4/9:16, avatar_ids, avatars, duration=15, generate_audio=False, hook_id, mode=ugc, product_ids, prompt, resolution=480p/720p/1080p, setting_id, web_product_ids |
| `minimax_hailuo` | Minimax Hailuo | prompt | duration=6/10, input_images, model=minimax/minimax-fast/minimax-2.3/minimax-2.3-fast, prompt, resolution=512/768/1080 |
| `reframe` | Reframe | aspect_ratio, medias | aspect_ratio=21:9/16:9/4:3/1:1/3:4/9:16, duration, folder_id, resolution=480p/720p/1080p |
| `sam_3_video` | Remove Background | medias | apply_mask=True, folder_id, frames_count, prompt= |
| `seedance1_5` | Seedance 1.5 Pro | prompt | aspect_ratio=auto/16:9/9:16/4:3/3:4/1:1/21:9, duration=4/8/12, generate_audio=True, prompt, resolution=480p/720p/1080p |
| `seedance_2_0` | Seedance 2.0 | prompt | aspect_ratio=auto/16:9/9:16/4:3/3:4/1:1/21:9, bitrate_mode=standard/high, duration=5, generate_audio=True, genre=auto/action/horror/comedy/noir/drama/epic, mode=std/fast, prompt, resolution=480p/720p/1080p/4k |
| `seedance_2_0_mini` | Seedance 2.0 Mini | prompt | aspect_ratio=auto/16:9/9:16/4:3/3:4/1:1/21:9, bitrate_mode=standard/high, duration=5, generate_audio=True, genre=auto/action/horror/comedy/noir/drama/epic, prompt, resolution=480p/720p |
| `topaz_video` | Topaz | - | aspect_ratio=auto/21:9/16:9/4:3/1:1/3:4/9:16, duration, enhancement, folder_id, frame_interpolation, frame_rate=30, frames_count, input_height, input_video, input_video_size=0, input_width, resolution=1080p/2160p |
| `veo3` | Google Veo 3 | input_image, prompt | aspect_ratio=16:9/9:16, input_image, model=veo-3-preview/veo-3-fast, prompt |
| `veo3_1` | Google Veo 3.1 | prompt | aspect_ratio=16:9/9:16, duration=4/6/8, input_image, model=veo-3-1-preview/veo-3-1-fast, prompt, quality=basic/high/ultra |
| `veo3_1_lite` | Google Veo 3.1 Lite | prompt | aspect_ratio=16:9/9:16/auto, duration=4/6/8, generate_audio=False, prompt |
| `video_background_remover` | Video Background Remover | medias |  |
| `video_deflicker` | Video Deflicker | input_video | duration, folder_id, input_video |
| `video_upscale` | Video Upscale | input_video | duration, folder_id, input_video |
| `voice_change` | voice_change | input_video, voice_id | folder_id, input_video, voice_id, voice_type=preset/element |
| `wan2_6` | Wan 2.6 Video | prompt | aspect_ratio=16:9/9:16/1:1, duration=5/10/15, prompt, quality=720p/1080p |
| `wan2_7` | Wan 2.7 | prompt | aspect_ratio=16:9/9:16/1:1/4:3/3:4, duration=5, prompt, resolution=720p/1080p |

## Playbook por agente

### João
- Criar variações visuais/reels/ads via Content OS
- Usar Virality Predictor antes de escala
- Nunca publicar automaticamente; entregar URL/asset para aprovação
### Jarvis
- Pode consultar este mapa e orquestrar qual skill/fluxo chamar
- Deve carregar ivs-data-dev-os antes de desenvolvimento ou integração Content OS
### Maria
- Governar uso, custos e compliance; pedir aprovação para publicação externa ou uso de rosto real
### Ana
- Revisar claims clínicos antes de conteúdo médico promissor; Higgsfield não decide compliance clínico
### Clara
- Não usar para atendimento direto; pode receber assets já aprovados via fluxos internos, sem envio automático

## Onde consultar os brutos

- `raw/README.md`, `raw/MODELS.md`, `raw/cli_help.txt`, `raw/cli_subcommands_help.txt`
- `raw/model_list_live.json`, `raw/model_get/*.json`, `raw/lists/*.json`
