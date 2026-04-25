# API reference

Endpoints, parameters, response shapes, error handling, and host-specific behavior for the gpt-image-2 model behind an OpenAI-compatible host.

## Model facts

- **Released:** April 2026.
- **Strengths:** instruction following on long prompts, multilingual text rendering (Chinese/Japanese/Korean), custom resolutions, precise local edits.
- **Constraints on this host (jmrai.net default):**
  - Quality tiers all cost the same — default `--quality high`.
  - Multi-image **input** in one /edits call is NOT supported. For composition, chain two edit calls.
  - `background=transparent` is NOT supported (returns HTTP 400 with `image_generation_user_error`). For sprites / icons / cutouts, use a chroma-key color in the prompt (e.g. `solid magenta #FF00FF background`) and remove client-side with `rembg` / ImageMagick / pngquant.
  - Resolution: max side `< 3840px`, aspect ratio `≤ 3:1`.

## Base URL

Default: `https://jmrai.net/v1`

Override via `OPENAI_IMAGE_BASE_URL` env var.

## Authentication

`Authorization: Bearer <key>` header, where `<key>` comes from `OPENAI_IMAGE_API_KEY` (or `OPENAI_API_KEY` as fallback).

## Endpoints

### POST /images/generations

Generate one image from a text prompt. JSON body.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `model` | string | yes | `gpt-image-2` |
| `prompt` | string | yes | Up to ~4000 chars; sweet spot 50–300 words for instructional prompts |
| `n` | int | no (default 1) | The script ignores host-side n>1 and parallelizes client-side instead — see § Parallel batching |
| `size` | string | no | `WxH`. Common: `1024x1024`, `1536x864`, `1536x1024`, `1024x1536`, `1024x1792`, `1792x1024`, `2048x2048`. Constraints: max side <3840, ratio ≤3:1 |
| `quality` | string | no | `low` / `medium` / `high` (or `standard` / `hd`). Default `high` on this script. Cost identical across tiers on this host |
| `style` | string | no | `vivid` / `natural` |
| `background` | string | no | `transparent` / `opaque` / `auto`. **NOT supported on jmrai.net host** — returns HTTP 400. Use chroma key in the prompt instead |
| `response_format` | string | no | `url` / `b64_json`. Script handles either |
| `user` | string | no | Optional client-side identifier passed through |

Response:

```json
{
  "created": 1730000000,
  "data": [
    { "url": "https://..." }
    // OR
    { "b64_json": "iVBORw0KGgo..." }
  ]
}
```

### POST /images/edits

Edit, mask-inpaint, or style-transfer an existing image. Multipart/form-data.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `model` | string | yes | `gpt-image-2` |
| `image` | file (PNG/JPEG) | yes | **One** file. This host does not accept multiple input images per call |
| `prompt` | string | yes | Use the `change ONLY X / preserve Y exactly / do not Z` pattern |
| `mask` | file (PNG with alpha) | no | White pixels = regenerate, transparent = keep |
| `n` | int | no | Same parallelization note as generations |
| `size` | string | no | Same constraints |
| `quality` | string | no | Default `high` |
| `background` | string | no | |
| `response_format` | string | no | |
| `user` | string | no | |

Same response shape as generations.

## Resolution constraints

| Property | Constraint |
|----------|------------|
| Max longest side | `< 3840px` |
| Max aspect ratio | `≤ 3:1` (long side / short side) |
| Min dimensions | reasonable (e.g. don't go below 256×256) |

The script (`scripts/gpt_image.py`) validates these upfront — fast failure with a clear message instead of an opaque API error.

## Quality tiers

| Tier | Use when |
|------|----------|
| `low` | Fast throwaway iteration; rough layout sanity-checks |
| `medium` | Daily default for casual generation |
| `high` | Default on this host (cost is identical). Mandatory for: dense text, infographics, close-up portraits, brand work |

On hosts where pricing differs, the choice matters more.

## Parallel batching (client-side)

The script's `-n N` flag fires N parallel single-image requests via `concurrent.futures.ThreadPoolExecutor`. This:

- Works regardless of whether the host supports `n>1` per request
- Achieves wall-clock speed close to a single request (subject to `--concurrency`, default 4)
- Lets the script print result paths as they complete

Example payload sent for each parallel call:

```json
{
  "model": "gpt-image-2",
  "prompt": "...",
  "n": 1,
  "size": "1024x1024",
  "quality": "high"
}
```

## Error codes

| Status | Meaning | Script behavior |
|--------|---------|-----------------|
| 400 | Bad request — invalid params | Surface immediately with body |
| 401 | Bad / missing key | Surface with reminder to set env var |
| 403 | Quota / billing | Surface; user checks balance with the host |
| 413 | Payload too large | Compress source images first (see post-process.md) |
| 429 | Rate limited | Auto-retry 4x with exponential backoff |
| 500–599 | Server error | Auto-retry 4x with exponential backoff |
| Other 4xx | Surface with body |

## Curl reference (only when the script is unavailable)

### Generate

```bash
curl https://jmrai.net/v1/images/generations \
  -H "Authorization: Bearer $OPENAI_IMAGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "a red panda eating bamboo, watercolor",
    "size": "1024x1024",
    "quality": "high",
    "n": 1
  }'
```

The response contains either a URL or a `b64_json` string. You'll need to download/decode it yourself — which is exactly why the Python script exists.

### Edit (single source image)

```bash
curl https://jmrai.net/v1/images/edits \
  -H "Authorization: Bearer $OPENAI_IMAGE_API_KEY" \
  -F "model=gpt-image-2" \
  -F "image=@./input.png" \
  -F "prompt=Edit the input: change ONLY the sky to a clear blue. Preserve everything else exactly." \
  -F "size=1024x1024" \
  -F "quality=high"
```

### Edit with mask

```bash
curl https://jmrai.net/v1/images/edits \
  -H "Authorization: Bearer $OPENAI_IMAGE_API_KEY" \
  -F "model=gpt-image-2" \
  -F "image=@./input.png" \
  -F "mask=@./mask.png" \
  -F "prompt=Fill the masked area with continuation of the cobblestone street, matching perspective and lighting." \
  -F "size=1024x1024"
```

## Tips for working with the API directly

- Some hosts return URLs that expire — download immediately, don't pass URLs around.
- Both `url` and `b64_json` are valid responses; the script normalizes — handle both if you must call directly.
- For multipart uploads from the shell, `curl -F` is the cleanest path.
- The `user` field is useful for the host's own rate-limiting / debugging — pass a stable per-user string when relevant.
- For batch runs, fire requests concurrently from the client (`xargs -P`, `parallel`, `ThreadPoolExecutor`, etc.) rather than asking the host for `n>1`.

## Versioning notes

This is an OpenAI-compatible host. The specific model `gpt-image-2` is provided by the host (jmrai.net by default). Behavior may diverge slightly from upstream — when in doubt, generate a small low-quality test before relying on a specific feature.

If migrating from a previous model (`gpt-image-1.5` or older), OpenAI's official guidance is: don't rewrite your prompt library. Run the same prompts on `gpt-image-2`, compare outputs, and tune only the ones that drifted.

## Anti-patterns to avoid in prompts

These were useful on pre-GPT-Image-2 models. Now they're noise (or worse):

| Pattern | What to do instead |
|---------|--------------------|
| `4K, 8K, ultra detailed, masterpiece` | Drop entirely. Use `--quality high` instead. |
| `trending on artstation` | Drop. Name a specific reference if you want a style. |
| `professional, beautiful, premium, stunning` | Replace with concrete spec language (font, lighting direction, palette). |
| Negative prompts like `lowres, error, bad anatomy, bad hands` | Drop. The model handles this without prompting; only state negatives that you specifically don't want (`no humans`, `no text`, etc.). |
| Stacking multiple style words | Pick ONE style anchor — a named artist, film, movement, or game. |
