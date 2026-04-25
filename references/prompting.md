# Prompting gpt-image-2

GPT Image 2 (April 2026) is not the same animal as the previous generation of image models. The old "magic word" approach — stacking *4K, 8K, ultra detailed, masterpiece, trending on artstation* — is at best useless and often actively makes outputs worse. The new model rewards precise, instructional prompts written like a product spec, not like an incantation.

This document teaches Claude how to write prompts that actually work for this model.

## What changed in GPT Image 2 (vs previous generations)

- **Strong instruction following.** Long prompts (50–300 words) don't lose detail anymore. Be specific.
- **Near-perfect text rendering**, including Chinese / Japanese / Korean. Quote the exact string.
- **Custom resolutions**: any WxH where max side < 3840px and aspect ratio ≤ 3:1.
- **Edit endpoint does precise local edits**: tell it what to change AND what to preserve.
- **Quality tiers exist**, but on this host all tiers cost the same — default `--quality high`.

## The canonical prompt structure

OpenAI's official Cookbook recommends this order. Following it makes the model translate your prompt much more reliably:

```
Intent / Use case  →  Scene / Background  →  Subject  →  Key details  →  Text content  →  Style language  →  Constraints
```

Worked example:

> *Create one **pitch-deck slide** titled "Q3 Revenue Performance" that looks like a real Series A board-meeting slide. Layout (landscape 16:9): title top-left in 36pt Inter dark gray, two-column body with a 60% bar chart on the left and three KPI cards on the right, footer with a logo placeholder bottom-right and page number "03". Chart: clean vertical bars for Q1–Q3 2026, y-axis $0–$8M, three bars at $3.2M, $4.8M, $6.5M, muted blue palette, subtle gridlines, no shadows. KPI cards show: "+34% YoY", "189 new accounts", "$42K ACV". Style: white background, Inter typography, tight spacing, no decorative elements, no clip art, no gradients, no stock photography.*

Notice what's NOT in there: no "highly detailed", no "8K", no "masterpiece", no "trending on artstation". Every word is doing concrete work.

## The seven habits of high-quality prompts

### 1. State the intent first

Open with what the image is FOR, not what's IN it. The model has different "modes" for different intents and your opening word selects the mode:

- *Create one pitch-deck slide titled…*
- *Create a realistic SaaS dashboard UI mockup for…*
- *Create a children's book illustration of…*
- *Create a product hero photograph of…*
- *Create a character reference sheet for a 2D platformer…*
- *Create a vertical infographic titled…*
- *Edit the input image: change ONLY [X]…*

This single change moves quality more than any style word you could add.

### 2. Quote the exact text

For every character that should appear in the image, quote it. Specify font style, weight, size, color, and position:

- ✅ `Headline (top center, 64pt bold sans-serif, dark gray): "造物时代"`
- ❌ `a poster about Maker Era`

For Chinese specifically, name the script flavor (`楷书`, `黑体`, `思源黑体风格`, `行书`) — and warn the model `no extra Chinese characters anywhere except the quoted text` to suppress decorative-looking nonsense.

### 3. Use photographic / spec language, not praise language

Praise language ("stunning, beautiful, ultra-detailed, professional, premium") tells the model nothing concrete and pushes outputs toward stock-photo-ad aesthetics. Spec language tells the model where to put things and what they look like.

| Replace | With |
|---------|------|
| "beautiful lighting" | "soft north-window light from the left, gentle wraparound fill" |
| "professional" | "Inter 14pt, 8px grid spacing, single accent color #6366F1" |
| "high quality" | "shot on 50mm f/2.8, fine 35mm grain, neutral white balance" |
| "detailed" | "visible ceramic glaze imperfections, fine wood grain on the counter" |
| "modern" | "flat vector, monoline 2px stroke, generous negative space, off-white background" |

### 4. Specify "change ONLY X / keep everything else" for edits

The edit endpoint is the killer feature, but only if you tell the model what to preserve. Without explicit preservation, lighting drifts, perspectives shift, faces change.

Template:

```
Edit the input image: replace ONLY [thing] with [new thing of same shape/proportions].

Preserve exactly:
- Camera angle and framing
- Room lighting and shadow direction
- Floor reflections and contact shadows
- All other furniture, walls, and decor
- Color temperature and white balance

Render: [new thing details].

Do not: add new objects, change saturation, restyle the room,
or alter any text or signage in the scene.
```

For people, add `input_fidelity="high"` (or, in this CLI, the `--quality high` default plus a `Preserve exactly: facial features, identity, hair, expression` block).

### 5. Pick the right resolution for the use case

| Use case | Size | Notes |
|----------|------|-------|
| PPT / web hero / YouTube thumbnail | `1536x864` (true 16:9) or `1792x1024` | Title-safe area on one side |
| Print poster, mobile cover, story | `1024x1536` (2:3) or `1024x1792` | Vertical typography |
| Square (icon, IG post, logo) | `1024x1024` | For sprites/icons that need transparency, ask for `solid magenta #FF00FF background` in the prompt and strip post-hoc — this host doesn't support `--background transparent` |
| High-res square / print poster | `2048x2048` | Slower; only when needed |
| Character / item portrait | `1024x1024` or `1024x1536` | Transparent bg for assets |
| Pixel-art tileset / sprite sheet | `2048x2048` displayed-at, but specify the actual pixel grid in the prompt | See use-cases.md |

Wrong aspect ratio = wasted generation. Decide BEFORE you write the prompt.

### 6. Iterate, don't stack

If the first generation is 80% there, **change ONE dimension** and re-generate. Don't bolt three new clauses onto the prompt — you won't know which one helped.

| If the result is… | Change THIS only |
|-------------------|------------------|
| Wrong vibe | Style anchor (named artist / movement / film) |
| Too generic | Composition (specific camera, angle, framing) |
| Lifeless | Lighting (direction + color temperature) |
| Cluttered | Negative space + remove adjectives |
| Off-brand color | Add hex codes or named palette |
| Text wrong | Re-quote the text and add `no extra characters` |

For exploration, fire 3–4 variants in parallel (`-n 4`) — cheaper than serial single calls.

### 7. Use `--quality high` by default on this host

Cost is the same across tiers on this host, so there's no reason to under-spec. Use `low`/`medium` only for fast throwaway iterations where speed matters more than fidelity (e.g. a quick layout sanity check).

## Style vocabulary (for when you DO want a style anchor)

A named reference beats five vague adjectives. Anchor to one of:

### Photography
*Annie Leibovitz (editorial), Steve McCurry (documentary), Wes Anderson (symmetric pastel), Gregory Crewdson (cinematic suburban), Henri Cartier-Bresson (decisive moment B&W), Tim Walker (theatrical fashion).*
*Film stocks*: Kodak Portra 400, CineStill 800T, Ilford HP5, Fuji Velvia.
*Lens / camera*: 50mm f/2.8, 85mm f/1.4, Hasselblad medium format, 16mm fisheye.

### Illustration
*Flat vector (à la Stripe / Linear marketing), isometric line art, children's book watercolor (Beatrix Potter), Art Nouveau (Mucha), Art Deco poster (Cassandre), Bauhaus geometric, Saul Bass mid-century, risograph two-color print, gouache spot illustration.*

### Anime / Asian art
*Studio Ghibli watercolor, Makoto Shinkai cinematic anime, Mamoru Hosoda warm tones, Pixiv illustration, traditional 浮世绘 ukiyo-e, 工笔画 Chinese gongbi, 水墨画 ink wash.*

### 3D / digital
*Blender Cycles claymation, Octane render, Unreal Engine 5 cinematic, low-poly PS1-era, voxel art, glassmorphism UI render.*

### Game / retro
*16-bit SNES pixel art, NES 8-bit limited palette, Game Boy 4-shade green, PICO-8 16-color, Stardew Valley pixel style, Hades vector painted, Hollow Knight hand-drawn.*

### Painting
*Oil painting in the style of John Singer Sargent, impressionist plein air (Monet), expressionist (Egon Schiele), baroque chiaroscuro (Caravaggio), Hopper americana, Rothko color field.*

**Rule of thumb**: if you can't name the style precisely, name the *reference* — an artist, a film, a movement, a magazine, a game.

## Composition vocabulary

| Need | Words |
|------|-------|
| Distance | extreme close-up, close-up, medium shot, full-body, wide shot, establishing shot |
| Angle | eye-level, low angle, high angle / bird's-eye, dutch tilt, over-the-shoulder |
| Framing | centered, rule of thirds, asymmetric, symmetrical, copy area on the [side] |
| 3D POV | front view, 3/4 view, isometric, top-down, side-profile, axonometric |
| Layout | generous negative space, tight crop, full bleed, vignette |
| Lens | shallow depth of field, fisheye distortion, tilt-shift, telephoto compression |

For posters and slides, **always** state where the negative space goes ("copy area on the right third for headline + subtitle").

## Lighting vocabulary

| Direction | Words |
|-----------|-------|
| Natural | golden hour, blue hour, harsh noon, overcast diffused, moonlit, north-window light |
| Studio | softbox key + rim light, three-point lighting, beauty dish, butterfly lighting |
| Mood | chiaroscuro, low-key (mostly shadow), high-key (mostly highlight), backlit silhouette |
| Color temp | warm tungsten, cool fluorescent, magenta neon, sodium street lamp, candlelight |
| Effects | volumetric god rays, lens flare, atmospheric haze, hard cast shadows |

Pick a single light direction with a single color temperature. Two light sources = okay, three = mush.

## Color & palette

State a palette explicitly:

- Named: *muted earth tones, monochrome blue, pastel mint and coral, jewel tones, sepia*
- Specific hex / Pantone: *cream #f5e6d3 background, deep navy #1a2b4c accent, single accent #6366F1*
- By reference: *Wes Anderson palette, 80s Memphis, Bauhaus primary red/yellow/blue*

For brand work, ask the user for hex codes before generating. Saves regen cycles.

## Negatives — say what NOT to include

GPT Image 2 obeys explicit negatives. Use them when the model keeps adding things you don't want:

- *no text, no watermarks, no logos*
- *no humans, no faces, no hands*
- *no extra fingers, no warped anatomy*
- *no busy background, plain backdrop*
- *no decorative gradients, no stock photography aesthetic*
- *no extra Chinese characters anywhere except the quoted text*

What you should NOT use as negatives:
- ~~lowres, bad anatomy, text, error~~ — these are old-model magic words; they're noise to GPT Image 2.

## Prompt template (copy / adapt)

```
Create a [INTENT — slide / poster / icon / illustration / mockup / photograph]
of [SUBJECT].

Layout: [where things go, sizes, alignment, negative space].

Text: [exact quoted strings, font style, size, color, position;
       OR: "no text".]

Style: [single named reference; OR: medium + era + adjectives].

Color: [palette by name or hex codes].

Lighting: [single direction + color temperature].

Constraints: [explicit negatives].
```

## Three habits that mark a pro prompt

1. **Open with intent**, not subject ("Create a pitch-deck slide…" beats "A chart and some KPIs").
2. **Quote every character** that should appear in the image, exactly once.
3. **Specify what to preserve** alongside what to change in every edit prompt.

## Anti-patterns to drop

| Don't write | Why |
|-------------|-----|
| "8K, 4K, ultra detailed, masterpiece" | Magic words from older models; ignored or harmful here |
| "trending on artstation" | Same |
| "professional, beautiful, premium, stunning" | Praise language with no instructional content |
| Long lists of stacked styles | "Watercolor + 3D + cyberpunk + manga" produces mush |
| Negative prompts like "lowres, error, bad anatomy" | Pre-GPT-Image-2 noise |
| Re-describing the whole image in an edit | The model already sees it; you're just shifting things |

## Cost / quality on this host

- All quality tiers cost the same → default `--quality high`.
- Use `--quality low` or `medium` only when iterating fast on rough comps where speed beats fidelity.
- For batch exploration, fire `-n 4 --concurrency 4` — 4 parallel hi-quality requests finishes in roughly the time of one.
