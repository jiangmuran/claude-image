---
name: gpt-image-2
description: Use when generating, editing, composing, or iterating on images — illustrations for reports/web, posters with Chinese or English typography, pitch-deck slides, UI mockups, infographics, pixel art, game sprites, character reference sheets, app icons, logo concepts, photoreal product shots, or photo edits with precise local changes. Symptoms include the user asking for "图", "图片", "插图", "海报", "封面", "图标", "ppt素材", "游戏素材", "改图", "修图", "logo", "draw me", "make an image", "生成一张", or attaching an image they want modified. Calls the gpt-image-2 model (April 2026 release; near-perfect text rendering including Chinese, custom resolutions up to 3840px, precise edits with preserve/change pattern) via OpenAI-compatible /images/generations and /images/edits endpoints.
---

# gpt-image-2

GPT Image 2 — released April 2026 — is the first generation that handles long instructional prompts cleanly, renders text correctly (Chinese / Japanese / Korean too), supports custom resolutions (max side < 3840px, ratio ≤ 3:1), and does precise local edits via the `change ONLY X / keep Y exactly` pattern.

This skill teaches you the prompt grammar, the workflow, and gives you a zero-dep CLI that handles auth, parallel batching, retries, and file IO.

## The contract

Always go through `scripts/gpt_image.py`. Don't curl the API directly — the script handles auth, retries, b64-vs-URL responses, multipart for edits, parallel single-image calls when batching, and writes files to disk for you. The user can't see images that only exist in the API response.

## Setup (once per machine)

Two environment variables:

```bash
export OPENAI_IMAGE_API_KEY="sk-..."                  # required
export OPENAI_IMAGE_BASE_URL="https://jmrai.net/v1"   # default; override only if user has a different host
```

If `OPENAI_IMAGE_API_KEY` is missing, the script exits with a clear message — ask the user for it, then suggest they add the export to `~/.zshrc`.

## Calling the script

Use the absolute path so it works from any working directory:

```bash
SKILL_DIR="$HOME/.claude/skills/gpt-image-2"   # adjust if installed elsewhere
GPT_IMG="python3 $SKILL_DIR/scripts/gpt_image.py"
```

### Env vars in Claude Code's Bash subshell

Claude Code's Bash tool runs **non-interactive shells that do NOT auto-source `~/.zshrc`**. If the user has the credentials in their shell rc and you get `ERROR: set OPENAI_IMAGE_API_KEY`, prefix every call with a source:

```bash
source ~/.zshrc 2>/dev/null && python3 $SKILL_DIR/scripts/gpt_image.py generate -p "..." -o ./out.png
```

Or, if the user provided the key in-conversation, pass it inline (don't write it to disk yourself):

```bash
OPENAI_IMAGE_API_KEY="sk-..." OPENAI_IMAGE_BASE_URL="https://jmrai.net/v1" \
  python3 $SKILL_DIR/scripts/gpt_image.py generate -p "..." -o ./out.png
```

Test once at the start of a session: `source ~/.zshrc && echo "${OPENAI_IMAGE_API_KEY:0:10}"`. If that prints a key prefix, you can safely use the source-prefix pattern for the rest of the session.

### Generate

```bash
$GPT_IMG generate \
  -p "<prompt>" \
  --size 1536x864 \
  -o ./hero.png
```

Defaults: `--quality high` (cost is identical across tiers on this host), `--size 1024x1024`.

### Edit (precise local change)

```bash
$GPT_IMG edit \
  -i ./input.png \
  -p "Edit the input image: change ONLY <X>. Preserve exactly: <Y>. Do not: <Z>." \
  -o ./edited.png
```

### Inpaint (mask-based)

White pixels in the mask = region to regenerate; transparent = keep.

```bash
$GPT_IMG edit -i ./photo.png --mask ./mask.png \
  -p "Fill the masked area with continuation of the cobblestone street, matching perspective and lighting." \
  -o ./inpainted.png
```

### Multiple variants in parallel

`-n N` fires N **parallel** single-image requests. Faster wall-clock than serial, and works regardless of host n>1 support.

```bash
$GPT_IMG generate -p "..." -n 4 --concurrency 4 -o ./out
# writes out-1.png … out-4.png
```

### What the host does NOT support

- **Multi-image input** (composing two source images in one /edits call). For composition, do it in two steps: generate or edit a base, then edit again with the next layer described. The script errors if you pass `-i` more than once.
- **Transparent backgrounds** (`--background transparent` returns HTTP 400). For sprites / icons / cutouts, use a **chroma-key color in the prompt** (`solid magenta #FF00FF background`) and remove it client-side after with `rembg` or ImageMagick (see `references/post-process.md`).
- Aspect ratios above 3:1 or sides ≥ 3840px. The script validates upfront.

Run `python3 $SKILL_DIR/scripts/gpt_image.py --help` (or `<subcommand> --help`) for every flag.

## Sizes — pick deliberately

| Use case | Size | Aspect |
|----------|------|--------|
| PPT slide / web hero / YouTube thumbnail | `1536x864` (true 16:9) or `1792x1024` | 16:9 / 7:4 |
| Square: app icon, social, logo, character portrait | `1024x1024` | 1:1 |
| High-res square / print poster | `2048x2048` | 1:1 |
| Mobile poster, story, vertical infographic, book cover | `1024x1536` | 2:3 |
| Tall mobile-first hero | `1024x1792` | 9:16ish |
| Wide cinematic banner | `1792x1024` | 16:9ish |

Wrong aspect ratio = wasted generation. Decide BEFORE writing the prompt.

## The workflow for any image task

1. **Clarify intent** only if truly ambiguous. Otherwise infer — auto mode means ship.
2. **Pick the right reference** for the use case (table below).
3. **Write the prompt** following the structure: *Intent → Scene → Subject → Details → Text → Style → Constraints*. See `references/prompting.md`.
4. **Pick size** from the table above.
5. **Call the script.** Save to a sensible path next to the user's project, not `/tmp`.
6. **VISUALLY VERIFY** — Read the saved PNG yourself. Check: does the text render correctly? Is the composition what you asked for? Did the style land? See § "Visual self-verification" below.
7. **Iterate** if the verification fails. Change ONE dimension and regenerate.
8. **Show the user** — Read the final PNG so it appears inline. Tell them the path.

## Visual self-verification (use your vision)

After every generation, before reporting success to the user, **Read the PNG yourself** and verify against the prompt:

- **Text:** Does each quoted string render exactly? No invented characters? Right font weight?
- **Layout:** Is the negative space where you asked for it? Is the subject on the right side of the frame if you said so?
- **Composition:** Right camera angle? Right framing? Centered if you said centered?
- **Style:** Did the named reference land, or did the model default to generic AI-soup?
- **Negatives obeyed:** No extra hands, no watermarks, no rogue text, no clutter you forbade?

If anything fails, iterate. **Change ONE dimension** (per `references/prompting.md` §6) and regenerate. Don't ship the user a bad result and ask them to verify — your vision is faster than their patience.

If you fired multiple variants (`-n 4`), pick the best one yourself before showing the user. Don't dump four files on them and ask them to choose unless they explicitly want options.

## When to load deeper references

Read these on demand — don't preload them.

| User wants | Read this |
|------------|-----------|
| Prompt-writing technique, style vocabulary, intent-first framework, anti-patterns to avoid | `references/prompting.md` |
| Concrete templates: pitch decks, UI mockups, posters, character sheets, infographics, logos, photoreal, edits | `references/use-cases.md` |
| Compress, resize, convert, combine, add text post-hoc | `references/post-process.md` |
| Full parameter list, error codes, custom-resolution constraints | `references/api.md` |

## Core prompt principles (cheat sheet)

The full guide is in `references/prompting.md`; the irreducible minimum:

1. **Open with intent**, not subject. *"Create a pitch-deck slide titled…"* beats *"A chart and some KPIs"*.
2. **Quote every character** that should appear, exactly once. For Chinese, name the script flavor (`黑体`, `楷书`, `思源黑体`).
3. **Use spec language, not praise language.** *"50mm f/2.8, soft north-window light from the left"* beats *"beautiful professional lighting"*.
4. **For edits: change ONLY X / preserve Y exactly.** Always state both.
5. **One style anchor**, not five. Name an artist, film, movement, or game.
6. **Drop the magic words.** *4K, 8K, ultra detailed, masterpiece, trending on artstation* — pre-GPT-Image-2 noise. Useless or harmful now.
7. **Default `--quality high`** (cost is the same on this host). Use lower tiers only for fast throwaway iteration.
8. **Iterate, don't stack.** One dimension change per regen.

## Self-check before calling the API

- [ ] Does the prompt open with intent (slide / poster / mockup / photograph / illustration)?
- [ ] Right aspect ratio for the use case?
- [ ] Did I quote every text string the user wants in the image?
- [ ] If this is an edit, am I describing the change AND what to preserve?
- [ ] Is the output path meaningful and discoverable?
- [ ] Am I about to type any of: `4K, 8K, masterpiece, trending on artstation, ultra detailed`? If yes — delete them.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| "Make me an image of a cat" | Open with intent, add style, composition, lighting. See prompting.md. |
| Generating in `/tmp` | Save next to user's project so they can find it. |
| Not Reading the result yourself | Visual self-verify EVERY time before showing the user. |
| Showing all `-n 4` variants without picking | Pick the best one yourself unless user asked for options. |
| Asking "what style?" when the user said "a poster" | Make a strong first attempt, then iterate. |
| Curl-ing the API directly | Use the script — handles retries, b64, multipart, parallel. |
| Forgetting Chinese text in quotes | Quote it exactly or model writes nonsense. |
| Stacking magic words | "Ultra detailed 8K masterpiece" makes outputs WORSE on GPT Image 2. |
| Re-describing the whole image in an edit | Describe ONLY the change + what to preserve. |
| Trying to compose two input images in one /edits call | Not supported on this host — chain two edit calls. |

## Freedom to be creative

These rules guide quality, not creativity. When the user says "surprise me" or leaves room:
- Pick a distinctive style with conviction (don't default to "modern minimalist")
- Push compositions: low angles, dutch tilts, asymmetric layouts, generous negative space
- Fire 3–4 parallel variants when exploring (`-n 4 --concurrency 4`) — same wall-clock as one
- For art briefs, propose a style direction in one sentence before generating, so the user can redirect cheaply

## Ship-quality bar

A result is ready to show the user when:

- ✅ Read-and-judged by you, not just generated
- ✅ Text (if any) renders exactly the quoted string
- ✅ Composition matches the prompt (subject placement, negative space, camera)
- ✅ Style landed (named reference is recognizable)
- ✅ No obvious AI failures (warped hands, melted text, ghost limbs)
- ✅ Saved at a path the user can find
