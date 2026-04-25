# gpt-image-2 — the skill that teaches your agent to actually use it

> Drop this into Claude Code or Codex. Your agent will go from "here's a curl command, good luck" to producing pitch-deck slides, Chinese posters, pixel-art tilesets, photoreal product shots, and surgical photo edits — first try, every try.

GPT Image 2 dropped in April 2026. It's a generational leap: long instructional prompts no longer lose detail, text rendering is finally correct (Chinese / Japanese / Korean too), custom resolutions go up to 3840px, and the edit endpoint does precise local edits via a `change ONLY X / preserve Y exactly` pattern.

But here's the catch: agents trained before April 2026 don't know any of this. They write prompts the old way — *"4K, ultra detailed, masterpiece, trending on artstation"* — which on GPT Image 2 is at best ignored and often actively harmful. They paste curl commands instead of saving files. They generate, then ask the user "does this look right?" instead of looking themselves.

This skill fixes all of that.

## What you get

```
gpt-image-2/
├── SKILL.md                # The entry point. Loaded automatically by the agent.
├── README.md               # You are here.
├── LICENSE                 # MIT.
├── install.sh              # One-command install for Claude Code.
├── .env.example            # Two env vars; that's the entire config.
├── references/
│   ├── prompting.md        # The 7 habits + intent-first framework + style vocab
│   ├── use-cases.md        # 10+ copy-paste templates: PPT slides, UI mockups,
│   │                       # Chinese posters, pixel art, character sheets,
│   │                       # infographics, logos, photoreal, photo edits…
│   ├── api.md              # Full parameter reference + custom-resolution rules
│   └── post-process.md     # Compress, resize, convert (pngquant/cwebp/avifenc)
└── scripts/
    └── gpt_image.py        # Zero-deps Python CLI (urllib only, Python 3.7+)
```

## Why your agent will actually use it

Three design decisions that make this load-bearing instead of decorative:

1. **Discoverable description.** The frontmatter `description` lists every symptom — "海报", "图标", "ppt素材", "改图", "draw me", "make an image" — so the agent's skill picker actually fires on image requests instead of falling back to ad-hoc curl.

2. **One CLI, four affordances.** Generate / edit / inpaint / batch-parallel are all the same script with subcommands. Auth, retries, b64-vs-URL, multipart, file IO, parallel batching — handled. Agents that try to roll their own usually get one of those wrong.

3. **Visual self-verification baked into the workflow.** The skill explicitly tells Claude to `Read` the generated PNG and judge it against the prompt before showing the user. No more "here's an image, hope it's right!"

## Install

### Claude Code (one-liner)

```bash
git clone https://github.com/<your-handle>/gpt-image-2.git ~/.claude/skills/gpt-image-2 \
  && bash ~/.claude/skills/gpt-image-2/install.sh
```

The installer asks for your API key, writes it to `~/.zshrc`, and offers a smoke test.

After install, Claude auto-discovers the skill on the next image request — no restart, no registration.

### Codex (or any agent that scans `~/.agents/skills/`)

```bash
git clone https://github.com/<your-handle>/gpt-image-2.git ~/.agents/skills/gpt-image-2 \
  && bash ~/.agents/skills/gpt-image-2/install.sh
```

Same skill, same script, same env vars. Codex's skill loader reads the same `SKILL.md` frontmatter.

### Manual / other agents / direct CLI use

```bash
git clone https://github.com/<your-handle>/gpt-image-2.git
cd gpt-image-2

# Set credentials in your shell rc
echo 'export OPENAI_IMAGE_API_KEY="sk-..."' >> ~/.zshrc
echo 'export OPENAI_IMAGE_BASE_URL="https://jmrai.net/v1"' >> ~/.zshrc
source ~/.zshrc

# Smoke test
python3 scripts/gpt_image.py generate \
  -p "a red panda eating bamboo, flat vector illustration, off-white background" \
  -o ./test.png
open test.png
```

For non-Claude agents, point your agent's instructions at `SKILL.md` — the markdown is self-contained and assumes only that the agent can call the script and Read PNG files.

## Credentials

Two environment variables. That's the entire config surface.

| Var | Required | Default |
|-----|----------|---------|
| `OPENAI_IMAGE_API_KEY` | yes | — |
| `OPENAI_IMAGE_BASE_URL` | no | `https://jmrai.net/v1` |

Falls back to `OPENAI_API_KEY` / `OPENAI_BASE_URL` if the image-specific ones aren't set — useful if you already use the same key for chat completions.

> **Don't commit your key.** `.gitignore` excludes `.env`. The `.env.example` is a template only.

## What it can do

A non-exhaustive sample (see `references/use-cases.md` for the full catalog with copy-paste templates):

- **Pitch-deck slides** — looks like a real Series A board slide, not "an illustration of a slide". Specific data, specific fonts, specific palettes. Multi-slide consistency via the edit endpoint.
- **Chinese posters & signage** — Spring Festival banners, product launches, event covers. Quoted text + script flavor (`楷书 / 黑体 / 思源黑体`) + "no extra Chinese characters" tail. Renders crisply.
- **Realistic UI mockups** — desktop dashboards, mobile screens, in real device frames with believable copy. Inter typography, hex-coded palettes, real-looking task names.
- **Pixel art & game assets** — character sprites, top-down tilesets (with chroma-key magenta backgrounds), item icons, character reference sheets with multiple views, environment concept art.
- **Infographics** — vertical info-dense diagrams that GPT Image 2 actually renders correctly. The "How an Espresso Machine Works" template is in `use-cases.md`.
- **Logo concepts** — 2x2 grids of variants exploring different shape languages. Vector-clean, no gradients, no 3D.
- **Photoreal product shots** — proper photo language (50mm f/2.8, north-window light, 35mm film grain) instead of "premium quality".
- **Surgical photo edits** — the `change ONLY X / preserve Y exactly` pattern. Object replacement, background swap, style transfer, mask-based inpainting.
- **Report figures & spot illustrations** — FT-style editorial diagrams, gouache section illustrations, app empty-state characters.

## How it teaches your agent to write prompts

The full guide is in `references/prompting.md`. The headline: **drop the magic words.**

Pre-GPT-Image-2 prompting was pattern-matching against training-data clichés:

```
beautiful stunning ultra-detailed 4K 8K masterpiece trending on artstation
cinematic lighting professional photography premium quality
```

GPT Image 2 doesn't reward this. It rewards instructional, specific, intent-first prompts:

```
Create a pitch-deck slide titled "Q3 Revenue Performance" that looks
like a real Series A board-meeting slide. Layout (16:9): title top-left,
36pt Inter dark gray. Two-column body: left 60% chart, right 40% three
KPI cards. Chart: vertical bars, Q1–Q3 2026, y-axis $0–$8M, three bars
at $3.2M, $4.8M, $6.5M, muted blue palette. KPI cards: "+34% YoY",
"189 new accounts", "$42K ACV". White background, Inter typography,
tight 8px grid, no clip art, no gradients, no stock photography.
```

Notice what's NOT there: no praise words, no "ultra detailed", no "8K". Every word is doing concrete instructional work.

The skill teaches Claude (or any agent) the canonical structure:

```
Intent / use case  →  Scene / background  →  Subject  →
  Key details  →  Text content  →  Style language  →  Constraints
```

Plus the seven habits: **state intent first, quote every character, use spec-language not praise-language, "change ONLY X / preserve Y" for edits, one style anchor not five, drop the magic words, iterate-don't-stack**.

## Why visual self-verification matters

A subtle but huge improvement: the skill tells Claude to **Read the generated PNG and judge it against the prompt** before showing the user. Did the text render correctly? Is the composition where you asked? Did the negatives get obeyed?

If anything fails, the agent iterates **one dimension at a time** (per the prompting guide) and regenerates. The user sees the *good* result, not "here's what I got, does it look right?"

This works because Claude *can* see images. It just doesn't, by default, look at things it generates. The skill changes that default.

## Architecture (the design choices)

A few things to notice if you're curious about the build:

- **Zero Python deps.** The CLI uses only `urllib`, `concurrent.futures`, `argparse`. No `requests`, no `openai`, no install dance. Runs on any Python 3.7+.
- **Parallel batching.** `-n 4` fires four parallel single-image requests rather than asking the API for n=4 in one call. Faster wall-clock, works regardless of host n>1 support.
- **Sane defaults.** `--quality high` by default (cost is identical across quality tiers on this host). `--size 1024x1024` default. `--concurrency 4` for parallel calls.
- **Upfront validation.** Resolution constraints (max side <3840px, ratio ≤3:1) checked before the API round-trip — fast failure, clear message.
- **Multi-image input gracefully refused.** This host's gpt-image-2 doesn't accept multiple input images per /edits call. The script errors with a clear workflow recommendation rather than silently failing.

All of these are reversible — fork it, change `DEFAULT_QUALITY` or `DEFAULT_BASE` or wire up an `--watermark` flag.

## Manual usage (no agent needed)

The CLI works on its own. Useful for batch jobs, scripts, or just exploring.

```bash
GI="python3 ~/.claude/skills/gpt-image-2/scripts/gpt_image.py"

# Generate
$GI generate -p "a misty mountain temple at dawn, Studio Ghibli watercolor" -o ./temple.png

# Four parallel variants
$GI generate -p "..." -n 4 --concurrency 4 -o ./out

# Edit / inpaint
$GI edit -i ./photo.png -p "Edit the input: replace ONLY the sky with northern lights. Preserve everything else exactly." -o ./aurora.png
$GI edit -i ./photo.png --mask ./mask.png -p "Fill the masked area with continuation of the road" -o ./fixed.png

# All flags
$GI generate --help
$GI edit --help
```

## Updating

```bash
cd ~/.claude/skills/gpt-image-2 && git pull
```

The skill is text + a script. No build step, no restart, no registration.

## Customizing for your team

Fork it. Pieces designed to be swapped:

- **`references/use-cases.md`** — add your house style, brand palettes, recurring asset templates (your own pitch-deck-slide template, your own brand-color hex codes, your own infographic format)
- **`scripts/gpt_image.py`** — add a `--watermark` flag, custom output naming, S3 upload, Slack post, whatever
- **`DEFAULT_BASE`** — point at your private gateway instead of the default
- **The system prompts your agent gets** — wire `SKILL.md` into your agent's bootstrap if it doesn't already auto-discover

Pull requests welcome if your additions are general-purpose. House-specific stuff stays in your fork.

## Roadmap (open issues / PRs)

- [ ] Optional `Pillow` integration for client-side image inspection (dimensions, format, alpha) before upload
- [ ] `--watermark` flag for signed outputs
- [ ] Cost estimator subcommand (when host pricing varies)
- [ ] Smarter default sizing based on prompt content (poster vs slide vs icon)
- [ ] Example gallery — community-submitted prompts + outputs

If you're interested in any of these, open an issue.

## License

MIT. See `LICENSE`. Use it however.

## Credits

Built for [Claude Code](https://claude.com/claude-code) but the pattern (markdown skill + zero-dep CLI + visual self-verification) works with any agent that can read files and call a script.

Inspiration: OpenAI's official GPT Image 2 Cookbook, Anthropic's superpowers/writing-skills patterns for agent-discoverable skills.
