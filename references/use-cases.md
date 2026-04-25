# Use cases — concrete prompts that work on gpt-image-2

For each use case: when to use, the template, a worked example, common pitfalls. Copy the templates and adapt — don't write from scratch.

The templates here are tuned for GPT Image 2 specifically. They follow the canonical structure (Intent → Scene → Subject → Details → Text → Style → Constraints), open with the use case as a noun ("Create a pitch-deck slide…"), and avoid the pre-GPT-Image-2 magic words.

> Pick aspect ratio FIRST. The size table in `SKILL.md` is the source of truth.

---

## PPT pitch-deck slide

The trick: tell the model to render *a real existing slide*, not "an illustration of a slide". Give specific data, specific fonts, specific spacing. Always landscape + `--quality high`.

### Template

```
Create one pitch-deck slide titled "<TITLE>" that looks like
a real <CONTEXT, e.g. Series A board-meeting> slide.

Layout (landscape 16:9):
- Title <position>, <font + size + color>
- <body breakdown — columns, charts, KPI cards, etc.>
- Footer: <logo placeholder + page number>

<Chart/component spec — exact axes, exact values, exact palette>

<KPI card content with exact strings>

Style: <background>, <typography>, <spacing>, no decorative elements,
no clip art, no gradients, no stock photography.
```

Size: `1536x864`. Quality: `high`.

### Worked example

> *Create one pitch-deck slide titled "Q3 Revenue Performance" that looks like a real Series A board-meeting slide.*
>
> *Layout (landscape 16:9): title top-left, modern sans-serif (Inter), 36pt, dark gray. Two-column body: left 60% chart, right 40% three KPI cards stacked vertically. Footer: company logo placeholder bottom-right, page number "03".*
>
> *Chart: clean vertical bar chart, Q1–Q3 2026, y-axis $0–$8M with $2M gridlines, three bars at $3.2M, $4.8M, $6.5M, muted blue palette, subtle gridlines, no shadows.*
>
> *KPI cards: large numbers with a one-line caption each: "+34% YoY", "189 new accounts", "$42K ACV".*
>
> *Style: white background, Inter typography throughout, tight 8px grid spacing, no decorative elements, no clip art, no gradients, no stock photography.*

### Multi-slide consistency

Generate slide 1. Then for slides 2+, use `edit` with `-i slide-1.png` and a prompt that says: *"Use the same layout system, typography, and color palette as the reference image. New title: '...'. New body: ..."*.

### Pitfalls

- Calling it "an illustration" → you get an illustrated slide, not a real-looking slide.
- Vague chart spec → numbers are nonsense. State the y-axis range and the bar values.
- Forgetting to forbid clip art / gradients → model adds AI-soup decoration.

---

## Realistic UI mockup

Treat it like a product description, not concept art. Mention specific components, spacing in pixels, font sizes, and **render it inside a device frame** for instant believability.

### Template

```
Create a realistic <desktop / mobile> <product type> UI mockup for
<product name>, a <one-line product description>.

Layout:
- <left sidebar / nav / header spec, with widths in px>
- <main content area: components, spacing, columns>
- <cards / list items / detail views with specific contents>

Visual system: <bg color>, <divider color hex>, <neutral palette>,
single accent color <#hex>, <font name and sizes for body / heading>,
<corner radius>, <border weight>, <shadow style>.

Render inside a realistic <device frame> with <environment description>.

No lorem ipsum: use believable real <task names / contents> like
"<example 1>", "<example 2>", "<example 3>".
```

### Worked example — desktop dashboard

> *Create a realistic desktop SaaS dashboard UI mockup for "Lattice", a project-management tool.*
>
> *Layout: Left sidebar 240px wide containing workspace logo, search bar, primary nav with icons (Inbox, Projects, Calendar, Team, Settings). Main area: top breadcrumb + filter chips, then a 3-column kanban board (To Do, In Progress, Done) with 4 cards in each column. Cards show: short title, owner avatar, due-date chip, priority dot, 1–2 tags.*
>
> *Visual system: white background, light gray dividers (#E5E7EB), neutral palette, single accent color #6366F1, Inter 14px body / 18px headings, rounded-lg corners, subtle 1px borders, no heavy shadows.*
>
> *Render inside a realistic 14-inch laptop frame on a clean wooden desk with soft natural light from the left.*
>
> *No lorem ipsum: use believable real task names like "Refactor auth flow", "Q4 OOO planning", "Design review – v2".*

Size: `1536x1024` for desktop, `1024x1536` with iPhone frame for mobile.

### Pitfalls

- Lorem ipsum text → looks fake. Always supply real-looking strings.
- No frame → looks like a flat illustration, not a product. Always frame.
- Vague typography → fonts come out generic. Name a font.

---

## Chinese text on posters

GPT Image 2 renders Chinese cleanly *if* you quote the exact characters and forbid extras.

### Template

```
Create a <orientation> <poster / banner / cover> for <purpose>.

Headline (top center, <font flavor>, <size + weight + color>): "<exact 中文>"
Subhead (below, lighter weight): "<exact 中文 or English>"

Background: <description>.
Decorative elements: <description, e.g. paper-cut motifs, 水墨 strokes, geometric shapes>.
Layout: <where the negative space goes>.

Color: <palette>.

No extra Chinese characters anywhere except the quoted text.
```

### Worked examples

**Spring Festival poster:**

> *Create a vertical Chinese New Year poster in modern paper-cut style. Headline (top center, 楷书 bold red, 96pt): "新春快乐". Subhead (smaller, below, 隶书 gold): "万事如意 阖家团圆". Background: layered red and gold paper-cut motifs of plum blossoms and lanterns, gradient from deep crimson to warm gold. Centered traditional Chinese knot ornament between headline and subhead. Generous negative space at the bottom for an organization name added later. No extra Chinese characters anywhere except the quoted text.*
>
> Size: `1024x1536`.

**Tech product launch banner:**

> *Create a horizontal product launch banner. Headline (left side, 思源黑体风格 large bold, dark gray): "智能办公,从这里开始". Tagline (under headline, lighter weight, neutral gray): "Pro 系列 全新发布". Right side: floating 3D render of a sleek silver laptop, soft top-down studio light, subtle reflection. Background: gradient from off-white to cool light gray. No icons, no extra text, no extra Chinese characters except the quoted strings.*
>
> Size: `1792x1024`.

### Pitfalls

- Long passages (>30 chars per line) → break into two lines or shorten copy.
- Mixing fonts in one line → pick one weight per line.
- Asking for "calligraphy" without specifying script → say *楷书 / 行书 / 隶书 / 黑体* explicitly.
- Forgetting the "no extra Chinese characters" tail → model adds decorative-looking nonsense.

---

## Pixel art & game assets

Pixel art needs explicit pixel-grid declaration; otherwise you get smooth illustration that "looks pixel-y".

### Character sprite

> *Create a 32x32 pixel art character sprite for a fantasy RPG, displayed at 1024x1024 for clarity. Limited 12-color palette inspired by Stardew Valley. Subject: young witch in a wide-brimmed hat holding a glowing potion bottle, front-facing idle pose, distinct silhouette readable at thumbnail size. Solid magenta #FF00FF background (chroma key for easy removal). Hard pixel edges, no anti-aliasing, no smooth gradients.*
>
> Size: `1024x1024`. Strip the magenta after with `rembg` or ImageMagick (see `post-process.md`). This host does NOT support `--background transparent`.

### Top-down tileset (with chroma key for easy chroma-key removal)

> *Create a top-down 32x32 pixel art tileset for a forest biome in a retro RPG. Include 16 tiles in a 4x4 grid, each separated by a 1px gap: grass, tall grass, dirt path, stone path, forest edge, log, mushroom, small flower, water edge (4 directions), rock cluster, tree stump, bush, fern, fallen log, dirt patch.*
>
> *Style: SNES-era pixel art, 16-color palette, crisp pixel edges, no anti-aliasing, no dithering above 2x2, seamless tileable edges where applicable.*
>
> *Background: solid #FF00FF magenta (chroma key).*
>
> Size: `2048x2048`.

### Item icon

> *Create a single 64x64 pixel art item icon: a glowing blue mana potion in a round-bottom flask with cork stopper. PICO-8 style limited 16-color palette. Centered on solid magenta #FF00FF background (chroma key for easy removal). Subtle inner highlight on the glass, hard pixel edges, no anti-aliasing.*
>
> Size: `1024x1024`. Use chroma key + post-strip — this host doesn't support `--background transparent`.

### Pitfalls

- Asking for pixel art at 1024px without saying "pixel grid" → smooth illustration.
- Trying to use `--background transparent` on this host → HTTP 400. Use chroma key (`#FF00FF`) in the prompt and strip post-hoc.
- Multiple distinct characters in one sprite → generate ONE per call, compose later.
- "8-bit" alone is ambiguous → say "NES-era 8-bit" or "Game Boy 4-shade green" explicitly.

---

## Game character reference sheet (multi-view)

GPT Image 2 can produce a single sheet with multiple consistent views — useful for handing off to riggers or modelers.

> *Create a character reference sheet for a 2D side-scroller game.*
>
> *Character: a young desert ranger, female, mid-twenties, sun-tanned skin, short ash-brown hair, wearing a sand-colored cloak over leather armor, crossbow on her back, utility belt with three pouches.*
>
> *Sheet layout: single image divided into three equal panels side by side on a flat warm-gray background. Panel 1: front view, neutral standing pose. Panel 2: 3/4 side view, weight on right leg. Panel 3: back view, showing cloak drape and crossbow.*
>
> *Style: hand-painted 2D fantasy illustration, limited palette (5–6 colors), soft cel shading, clean outline, consistent proportions across all three panels, character height identical in each panel.*
>
> *No background scenery, no text labels, no shadow ground plane.*
>
> Size: `1792x1024`.

### Keeping the same character across multiple shots

Generate the reference sheet first. Then for new shots, use `edit -i sheet.png` with prompt: *"Use the same character (same outfit, proportions, color palette, facial features) but in a new scene where she is [...]"*.

### Game environment concept

> *Create environment concept art for a stealth game level. Painted illustration in a Dishonored / Arkane art-direction style. Subject: a fog-shrouded cobblestone alley at night between leaning Victorian-era buildings, single gas lamp casting a warm pool of light, distant figure barely visible at the far end. Wide cinematic composition. Palette: cool teal and deep purple shadows, warm amber lamp light as the only warm tone. Painterly brushwork, atmospheric depth. No characters in foreground, no text.*
>
> Size: `1792x1024`.

### Item card (Magic / Hearthstone style)

> *Create item card illustration for a card game, painted in a Magic the Gathering style. Subject: an ancient bronze key with intricate scrollwork and a glowing blue gem in the bow. Centered on a dark midnight blue background with subtle nebula texture. Soft inner light radiating from the key. Painterly brushwork visible, fine details on the key. No card frame, no text — just the artwork.*
>
> Size: `1024x1024`.

---

## Infographic (vertical, info-dense)

This is where GPT Image 2 leaves previous models in the dust — dense text + complex structure now actually works.

### Template

```
Create a vertical infographic titled "<TITLE>" for <audience / purpose>.

Layout (portrait 2:3):
- Title bar at top: <bg color>, <text color>
- <N> labeled stages flowing top to bottom with arrows:
  1. <stage>
  2. <stage>
  ...
- Each stage: <icon position>, <text spec>
- Footer with <one-line tip>: "<exact text>"

Style: <art direction>, <palette>, clean typography,
generous white space, thin line icons, no photographic elements,
no decorative clutter.
```

### Worked example

> *Create a vertical infographic titled "How an Espresso Machine Works" for café staff training.*
>
> *Layout (portrait 2:3): title bar at top, dark brown background, white text. Five labeled stages flowing top to bottom with arrows: (1) Bean hopper → grinder, (2) Grounds → portafilter (showing tamp), (3) Water tank → boiler (98°C), (4) Pump → 9 bar pressure → group head, (5) Extraction → 25–30 second shot into cup. Each stage: small isometric icon on the left, two-line description on the right. Footer with one quick tip: "Pro tip: weigh your shots — 1g in : 2g out".*
>
> *Style: flat vector look, warm coffee palette (cream, brown, terracotta accent), clean Inter typography, generous white space, thin line icons, no photographic elements, no decorative clutter.*
>
> Size: `1024x1536`. Quality: `high` (mandatory for legible body text).

### Pitfalls

- Skipping the title → model adds its own (often nonsense) heading.
- Forgetting to forbid photographic elements → it mixes painted and vector styles.
- Body-copy invisible → always `--quality high` for infographics.

---

## Logo / brand mark concepts

Generate **a grid of variants in one call** rather than one logo. Lets you compare directions cheaply.

### Template

```
Create <N> original logo concepts for "<COMPANY>", a <one-line description>.

Brand personality: <3–5 adjectives that aren't "professional/modern/clean">.

Constraints:
- Vector-style flat design, no gradients, no 3D, no shadows
- Strong silhouette readable at 16px
- Balanced negative space
- Single accent color allowed (<color cue>)
- Each variant explores a different shape language:
  wordmark, monogram, illustrative mark, badge

Output: <N> logos arranged in a <grid layout> on plain off-white background,
generous padding, no watermarks, no extraneous text,
no copyright-protected elements (no recognized brand similarities).
```

### Worked example

> *Create 4 original logo concepts for "Field & Flour", a small-batch artisan bakery.*
>
> *Brand personality: warm, timeless, handcrafted, unpretentious, slightly rustic.*
>
> *Constraints: vector-style flat design, no gradients, no 3D, no shadows. Strong silhouette readable at 16px. Balanced negative space. Single accent color allowed (warm wheat / muted sage). Each variant explores a different shape language: wordmark, monogram, illustrative mark, badge.*
>
> *Output: 4 logos arranged in a 2x2 grid on plain off-white background, generous padding, no watermarks, no extraneous text, no copyright-protected elements (no Disney, no recognized brand similarities).*
>
> Size: `1024x1024`.

For independent variants instead of a grid: use `-n 4 --concurrency 4` to fire four parallel single-logo requests.

### Pitfalls

- Asking for a logo with the company name → text often warps. Generate the mark, add text in vector software.
- "Modern" + "minimalist" + "professional" stacked → meaningless. Pick distinctive personality words.
- Multi-color logos rarely work first try — start monochrome, add color later.

---

## Photorealistic product / hero shots

Replace praise language with **proper photographic terms**. This is the single biggest unlock for realism.

### Template

```
Create a photorealistic product shot of <SUBJECT> on <SETTING>.

Camera: <lens>, <f-stop>, <eye level / angle>.
Lighting: <single direction + color temperature>, <fill description>,
no studio reflectors / no studio reflectors as needed.
Detail: <visible imperfections, materials, micro-details>.
Color: <white balance + grading note>.

Style: editorial <food / product / portrait> photography,
shallow depth of field, 35mm film grain, natural color grading.

No props beyond what's described, no text, no watermark.
```

### Worked example

> *Create a photorealistic product shot of a ceramic pour-over coffee dripper on a worn oak kitchen counter.*
>
> *Camera: 50mm lens, f/2.8, eye-level, slight 3/4 angle from the right.*
> *Lighting: soft morning window light from the left, natural shadow falloff to the right, no studio reflectors.*
> *Detail: visible ceramic glaze imperfections, fine wood grain on the counter, a single steam wisp rising from the dripper, a folded paper filter inside.*
> *Color: neutral white balance, no warm cast.*
>
> *Style: editorial food photography, shallow depth of field, 35mm film grain, natural color grading.*
>
> *No props beyond what's described, no text, no watermark.*
>
> Size: `1024x1536` for portrait product shots, `1792x1024` for environmental.

### Anti-soup tactics

Add to the prompt to fight the "AI photo" look:

- *candid, unposed, everyday detail, no glamorization*
- *natural color grading, no Instagram filter*
- *no perfect symmetry, slight imperfection in arrangement*
- *visible texture and grain, no plastic skin smoothing*

---

## Photo editing — the preserve / change pattern

The edit endpoint is GPT Image 2's killer feature. The rule is: *describe ONLY what changes, AND list everything you want preserved exactly.*

### Template

```
Edit the input image: change ONLY <X> with <new X of same shape/proportions>.

Preserve exactly:
- Camera angle and framing
- <subject identity / lighting direction / shadow falloff / scale>
- All other <objects in frame>
- Color temperature and white balance

Render: <new X details>.

Do not: add new objects, change saturation, restyle the scene,
or alter any text or signage in the scene.
```

### Worked examples

**Object replacement:**

```bash
$GPT_IMG edit -i ./room.png \
  -p 'Edit the input image: replace ONLY the white plastic chairs with solid oak wood chairs of the same shape and proportions. Preserve exactly: camera angle and framing, room lighting and shadow direction, floor reflections and contact shadows, all other furniture, walls, and decor, color temperature and white balance. Render: realistic oak grain, subtle satin finish, natural contact shadows beneath each chair leg. Do not: add new objects, change saturation, restyle the room, or alter any text or signage in the scene.' \
  -o ./room-oak.png
```

**Background swap:**

```bash
$GPT_IMG edit -i ./headshot.png \
  -p 'Edit the input image: replace ONLY the background with a softly blurred professional bookshelf. Preserve exactly: subject face, hair, expression, clothing, hairline, lighting on the face. Render: warm tungsten light from the left matching the existing skin tones, shallow depth of field on the bookshelf. Do not: alter the subject in any way, no resizing, no facial smoothing.' \
  -o ./headshot-bookshelf.png
```

**Mask-based inpainting (object removal):**

Make a mask PNG where white = area to fill, transparent = keep. Then:

```bash
$GPT_IMG edit -i ./photo.png --mask ./mask.png \
  -p 'Fill the masked area with continuation of the cobblestone street, matching perspective, lighting, and existing wear pattern. Preserve everything outside the mask exactly.' \
  -o ./photo-cleaned.png
```

**Style transfer (preserve composition, change rendering):**

```bash
$GPT_IMG edit -i ./photo.png \
  -p 'Convert the input image into a Studio Ghibli watercolor illustration. Preserve exactly: composition, subject pose, framing, head turn, hand position. Change ONLY: rendering style. Render: hand-drawn linework, soft pastel watercolor wash, gentle paper texture. Do not: change the pose, add new elements, or alter the framing.' \
  -o ./photo-ghibli.png
```

### Pitfalls

- Re-describing the whole image → model averages your description with what it sees, everything drifts.
- Forgetting "preserve exactly" → lighting, perspective, identity all shift subtly.
- Editing tiny details on a low-res input → upscale first or accept some drift.

---

## Web spot illustrations

For empty-states, section headers, marketing pages.

> *Create a spot illustration for a finance app empty-state. Flat vector style with subtle grain texture. Subject: a friendly cartoon piggy bank wearing reading glasses, holding a tiny chart. Centered on solid magenta #FF00FF background (chroma key for easy removal). No shadow. Palette: brand green #00b894 for the piggy bank, soft yellow for accents, no other colors besides the magenta key. Friendly approachable tone, single character, no background scenery.*
>
> Size: `1024x1024`. Strip the magenta with `rembg` for true transparency (this host doesn't support `--background transparent`).

---

## Report figures

For embedding in reports, white papers, slide decks. Aim for FT / Economist editorial cleanliness.

### Process diagram (no labels — added later in document)

> *Create a clean editorial diagram illustrating a 4-step user-onboarding flow. Style inspired by Financial Times graphics: flat geometric shapes, thin connecting arrows, generous whitespace. Layout: four circular nodes in a horizontal row connected by thin curved arrows. Each node contains a simple icon: (1) magnifying glass, (2) document with checkmark, (3) credit card, (4) party popper. Palette: deep navy #1a3a5c for shapes, warm orange #ff6b35 for arrows and accents, white background. No text labels — labels will be added in the document later.*
>
> Size: `1792x1024`.

### Section illustration for a long-form report

> *Create an editorial illustration for a sustainability-report section about ocean conservation. Style: textured gouache painting with visible brush strokes, slightly muted color. Subject: a humpback whale gliding through deep blue water with shafts of light from above, small school of fish in the foreground. Wide horizontal composition. Palette: deep teal and ultramarine with warm amber light beams. Calm contemplative mood. No text.*
>
> Size: `1792x1024`.

---

## App icons

> *Create a modern flat app icon for a meditation app. Centered single subject: stylized lotus flower made of overlapping translucent petals. Soft gradient background from dawn pink to sky blue. Subtle inner glow. Square format, designed to be readable at 64px. Palette: warm pink #ffb3ba, sky blue #b3d9ff, white highlights. No text, no extra ornaments.*
>
> Size: `1024x1024`.

### Icon set (matched style)

> *Create a set of 9 minimalist outline icons in a 3x3 grid on a white background. Theme: smart home. Icons: thermostat, light bulb, lock, camera, doorbell, speaker, plug, sensor, key. Style: monoline 2px stroke, rounded corners, no fill, all the same visual weight. Single color: charcoal #2c2c2c. Each icon centered in its grid cell with even padding.*
>
> Size: `2048x2048`.

---

## Quick recipes — when the user gives a vague brief

Default to one of these instead of asking.

| User says | Use |
|-----------|-----|
| "Something for my homepage" | 16:9 abstract gradient + single geometric focal element + brand palette |
| "Make me a poster" | 1024x1536 portrait, headline area top, focal element below, single style anchor |
| "A cool image" | Editorial photograph, Annie Leibovitz reference, 50mm lens, single light direction |
| "Make me a logo" | 4-variant grid in monochrome, ask for company name + industry first |
| "Generate art" | "Studio Ghibli watercolor of [their environment]" — cozy and reliably likable |
| "Game art" | Pick a reference (Hades, Hollow Knight, Stardew Valley), commit to it |
| "Help me with a presentation" | One hero illustration per section with consistent flat-vector style across all of them |
| "Make me a slide" | Pitch-deck slide template above with placeholder data |

---

## After generation: verify visually

For every result, **Read the saved PNG and judge it**:

- Did each quoted text string render exactly?
- Is composition / negative space where you specified?
- Did the named style anchor land?
- No warped hands / melted text / ghost limbs?

If any check fails, change ONE dimension (per `prompting.md` §6) and regenerate. Don't ship a result you haven't looked at.
