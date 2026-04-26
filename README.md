# Claude image

> 教 Claude Code、Codex 等 agent 真正用好 GPT Image 2 的 drop-in skill 包。
> A drop-in skill that teaches Claude Code, Codex, and other agents to actually use GPT Image 2.

[简体中文](#简体中文) · [English](#english)

---

## 简体中文

> 把这玩意儿丢进 Claude Code 或 Codex，你的 agent 就能从「这是个 curl 命令，祝你好运」进化成一次到位地产出 pitch deck 幻灯片、中文海报、像素图块、写实产品图、外科手术级修图。

GPT Image 2 是 2026 年 4 月发布的——这一代是分水岭：长指令式 prompt 不再丢细节，文字渲染终于正确（中日韩通吃），自定义分辨率最长 3840px，编辑端点用 `change ONLY X / preserve Y exactly` 模式做精准局部修改。

但是问题来了：2026 年 4 月之前训练的 agent 一无所知。它们用老办法写 prompt——*"4K, ultra detailed, masterpiece, trending on artstation"*——这些词在 GPT Image 2 上要么被忽略，要么直接帮倒忙。它们粘 curl 命令而不存文件。它们生成完之后问用户"这看着对吗？"，根本不自己看一眼。

这个 skill 把这些全修了。

### 仓库结构

```
gpt-image-2/
├── SKILL.md                # 入口。Claude 自动加载。
├── README.md               # 你正在看的这个。
├── LICENSE                 # MIT。
├── install.sh              # Claude Code 一键安装。
├── .env.example            # 两个环境变量,就这一点配置。
├── references/
│   ├── prompting.md        # 7 条习惯 + 意图优先框架 + 风格词表
│   ├── use-cases.md        # 10+ 复制即用模板:PPT 幻灯片、UI mockup、
│   │                       # 中文海报、像素图、角色三视图、信息图、
│   │                       # logo、写实摄影、修图……
│   ├── api.md              # 完整参数 + 自定义分辨率约束
│   └── post-process.md     # 压缩、缩放、转码 (pngquant/cwebp/avifenc)
└── scripts/
    └── gpt_image.py        # 零依赖 Python CLI (只用 urllib,Python 3.7+)
```

### 为什么你的 agent 真的会去调用它

三个让这玩意儿真正起作用而不是装饰品的设计:

1. **可发现的 description**。frontmatter 里把所有触发词都列了——"海报"、"图标"、"ppt素材"、"改图"、"draw me"、"make an image"——所以 agent 的 skill 选择器在收到图像请求时真的会触发,而不是退回去自己拼 curl。

2. **一个 CLI,四种能力**。生成 / 编辑 / 局部重绘 / 并行批处理都是一个脚本的子命令。鉴权、重试、b64 vs URL、multipart、文件 IO、并行批处理——都处理好了。Agent 自己手撸基本上某一项会出错。

3. **视觉自验证写进了工作流**。Skill 明确告诉 Claude 在把结果给用户之前自己 `Read` 一下生成的 PNG,对照 prompt 检查。再也不会出现"图给你了,你看对不对"。

### 安装

#### Claude Code(一行)

```bash
git clone https://github.com/jiangmuran/claude-image.git ~/.claude/skills/gpt-image-2 \
  && bash ~/.claude/skills/gpt-image-2/install.sh
```

安装脚本会问你要 API key,写到 `~/.zshrc`,可选跑一个冒烟测试。

装完之后下一次有图像请求 Claude 自动发现 skill——不用重启,不用注册。

#### Codex(或任何扫描 `~/.agents/skills/` 的 agent)

```bash
git clone https://github.com/jiangmuran/claude-image.git ~/.agents/skills/gpt-image-2 \
  && bash ~/.agents/skills/gpt-image-2/install.sh
```

同一个 skill,同一个脚本,同一组环境变量。

#### 手动 / 其他 agent / 直接命令行

```bash
git clone https://github.com/jiangmuran/claude-image.git
cd gpt-image-2

echo 'export OPENAI_IMAGE_API_KEY="sk-..."' >> ~/.zshrc
echo 'export OPENAI_IMAGE_BASE_URL="https://jmrai.net/v1"' >> ~/.zshrc
source ~/.zshrc

python3 scripts/gpt_image.py generate \
  -p "a red panda eating bamboo, flat vector illustration, off-white background" \
  -o ./test.png
open test.png
```

### 凭据

两个环境变量。配置就这么多。

| 变量 | 必填 | 默认值 |
|------|-----|--------|
| `OPENAI_IMAGE_API_KEY` | 是 | — |
| `OPENAI_IMAGE_BASE_URL` | 否 | `https://jmrai.net/v1` |

如果没设置 image 专用的两个,会回退到 `OPENAI_API_KEY` / `OPENAI_BASE_URL`——如果你已经在用同一个 key 跑 chat completions 这就很方便。

**自建反代image 2的API 原生支持此skill >_< ** https://order.jmrai.net

> **不要把 key commit 进去。** `.gitignore` 已经排除了 `.env`。`.env.example` 只是模板。

### 它能做什么

非完整列表(完整模板看 `references/use-cases.md`):

- **Pitch-deck 幻灯片** — 长得像真正的 Series A 董事会幻灯片,而不是"画一张幻灯片的插图"。具体数据、具体字体、具体配色。多页一致性靠 edit endpoint。
- **中文海报和招贴** — 春节海报、产品发布、活动封面。引号里的精确文字 + 字体类型(`楷书 / 黑体 / 思源黑体`)+ "no extra Chinese characters" 收尾。渲染干净。
- **写实 UI mockup** — 桌面 dashboard、移动端,放在真实设备外框里,文案写得像真的。Inter 字体、十六进制配色、合理的任务名。
- **像素图和游戏素材** — 角色 sprite、俯视图块集(用品红色 chroma key)、物品图标、角色三视图、场景概念图。
- **信息图** — GPT Image 2 真正能渲染的密集文字 + 复杂结构。`use-cases.md` 里有"How an Espresso Machine Works"模板。
- **Logo 概念** — 2x2 变体网格,探索不同形状语言。Vector clean、无渐变、无 3D。
- **写实产品图** — 用真正的摄影术语(50mm f/2.8、北窗光、35mm 胶片颗粒)代替"高品质"。
- **外科手术级修图** — `change ONLY X / preserve Y exactly` 模式。物体替换、背景换、风格迁移、mask 局部重绘。
- **报告插图和点缀图** — FT 风格编辑图、水粉章节插图、app 空状态角色。

### 它怎么教 agent 写 prompt

完整指南在 `references/prompting.md`。一句话:**抛掉魔法咒语**。

GPT Image 2 之前的 prompt 工程基本上是在和训练数据里的口水话做模式匹配:

```
beautiful stunning ultra-detailed 4K 8K masterpiece trending on artstation
cinematic lighting professional photography premium quality
```

GPT Image 2 不奖励这一套。它奖励指令式、具体、意图优先的 prompt:

```
Create a pitch-deck slide titled "Q3 Revenue Performance" that looks
like a real Series A board-meeting slide. Layout (16:9): title top-left,
36pt Inter dark gray. Two-column body: left 60% chart, right 40% three
KPI cards. Chart: vertical bars, Q1–Q3 2026, y-axis $0–$8M, three bars
at $3.2M, $4.8M, $6.5M, muted blue palette. KPI cards: "+34% YoY",
"189 new accounts", "$42K ACV". White background, Inter typography,
tight 8px grid, no clip art, no gradients, no stock photography.
```

注意里面**没有**:没有夸赞词、没有"ultra detailed"、没有"8K"。每一个词都在做具体的指令性工作。

Skill 教 Claude(或任何 agent)规范结构:

```
意图 / 用途  →  场景 / 背景  →  主体  →
  关键细节  →  文字内容  →  风格语言  →  约束条件
```

加上 7 条习惯:**意图开头、所有文字加引号、用规格语言不用夸赞语言、修图永远"change ONLY X / preserve Y"、一个风格锚点不要五个、抛掉魔法咒语、迭代不要堆砌**。

### 视觉自验证为什么重要

一个细微但巨大的改进:skill 让 Claude **自己 `Read` 生成的 PNG 并对照 prompt 判断**,然后再给用户看。文字渲染对了吗?构图在你说的位置吗?negative 听话了吗?

如果哪个不对,agent 会**一次只改一个维度**(参考 prompting 指南)然后重新生成。用户看到的是*合格*的结果,而不是"我生成了个东西,你看对不对"。

这个能 work 是因为 Claude *能*看图。它只是默认不会去看自己生成的东西。Skill 改的就是这个默认。

### 架构(几个设计选择)

如果你对实现细节感兴趣:

- **零 Python 依赖**。CLI 只用 `urllib`、`concurrent.futures`、`argparse`。没有 `requests`、没有 `openai`,没有装包步骤。任何 Python 3.7+ 都能跑。
- **客户端并行**。`-n 4` 是发 4 个并行的 n=1 请求,而不是请求 host 一次返回 4 张图。墙钟时间快、不用管 host 是否支持 n>1。
- **合理的默认值**。`--quality high`(这个 host 各档质量同价)。`--size 1024x1024`。`--concurrency 4`。
- **预先验证**。分辨率约束(最长边 <3840px、比例 ≤3:1)在请求 API 之前检查——快速失败、信息明确。
- **多图输入优雅拒绝**。这个 host 的 gpt-image-2 不接受一次 /edits 调用传多张输入图。脚本明确报错并给出工作流建议,而不是默默失败。

这些都可以改——fork 之后改 `DEFAULT_QUALITY` 或 `DEFAULT_BASE`,或者加个 `--watermark` flag。

### 不靠 agent 直接用

CLI 本身可以单独跑。批处理、脚本、手动探索都好用。

```bash
GI="python3 ~/.claude/skills/gpt-image-2/scripts/gpt_image.py"

# 生成
$GI generate -p "a misty mountain temple at dawn, Studio Ghibli watercolor" -o ./temple.png

# 4 张并行变体
$GI generate -p "..." -n 4 --concurrency 4 -o ./out

# 修图 / 局部重绘
$GI edit -i ./photo.png -p "Edit the input: replace ONLY the sky with northern lights. Preserve everything else exactly." -o ./aurora.png
$GI edit -i ./photo.png --mask ./mask.png -p "Fill the masked area with continuation of the road" -o ./fixed.png

# 所有 flag
$GI generate --help
$GI edit --help
```

### 更新

```bash
cd ~/.claude/skills/gpt-image-2 && git pull
```

Skill 就是文本 + 一个脚本。无构建、无重启、无注册。

### 给你的团队定制

Fork 一份。设计上可以替换的部分:

- **`references/use-cases.md`** — 加你们自家风格、品牌色卡、常用素材模板(自家的 pitch-deck 模板、自家的品牌 hex、自家的信息图格式)
- **`scripts/gpt_image.py`** — 加 `--watermark` flag、自定义输出命名、S3 上传、Slack 推送、随便加
- **`DEFAULT_BASE`** — 指向你们的私有网关而不是默认值
- **agent 拿到的 system prompt** — 如果你们的 agent 不会自动发现就把 `SKILL.md` 接进 bootstrap

通用的改动欢迎 PR。团队特定的留在你的 fork 里。

### License

MIT。看 `LICENSE`。随便用。

### 致谢

为 [Claude Code](https://claude.com/claude-code) 而做,但这个模式(markdown skill + 零依赖 CLI + 视觉自验证)适用于任何能读文件 + 调脚本的 agent。

灵感:OpenAI 官方 GPT Image 2 Cookbook,Anthropic superpowers/writing-skills 关于 agent 可发现 skill 的模式。

---

## English

> Drop this into Claude Code or Codex. Your agent will go from "here's a curl command, good luck" to producing pitch-deck slides, Chinese posters, pixel-art tilesets, photoreal product shots, and surgical photo edits — first try, every try.

GPT Image 2 dropped in April 2026. It's a generational leap: long instructional prompts no longer lose detail, text rendering is finally correct (Chinese / Japanese / Korean too), custom resolutions go up to 3840px, and the edit endpoint does precise local edits via a `change ONLY X / preserve Y exactly` pattern.

But here's the catch: agents trained before April 2026 don't know any of this. They write prompts the old way — *"4K, ultra detailed, masterpiece, trending on artstation"* — which on GPT Image 2 is at best ignored and often actively harmful. They paste curl commands instead of saving files. They generate, then ask the user "does this look right?" instead of looking themselves.

This skill fixes all of that.

### What you get

```
gpt-image-2/
├── SKILL.md                # The entry point. Loaded automatically by the agent.
├── README.md               # You are here.
├── LICENSE                 # MIT.
├── install.sh              # One-command install for Claude Code.
├── .env.example            # Two env vars; that's the entire config.
├── references/
│   ├── prompting.md        # 7 habits + intent-first framework + style vocab
│   ├── use-cases.md        # 10+ copy-paste templates: PPT slides, UI mockups,
│   │                       # Chinese posters, pixel art, character sheets,
│   │                       # infographics, logos, photoreal, photo edits…
│   ├── api.md              # Full parameter reference + custom-resolution rules
│   └── post-process.md     # Compress, resize, convert (pngquant/cwebp/avifenc)
└── scripts/
    └── gpt_image.py        # Zero-deps Python CLI (urllib only, Python 3.7+)
```

### Why your agent will actually use it

Three design decisions that make this load-bearing instead of decorative:

1. **Discoverable description.** The frontmatter `description` lists every symptom — "海报", "图标", "ppt素材", "改图", "draw me", "make an image" — so the agent's skill picker actually fires on image requests instead of falling back to ad-hoc curl.

2. **One CLI, four affordances.** Generate / edit / inpaint / batch-parallel are all the same script with subcommands. Auth, retries, b64-vs-URL, multipart, file IO, parallel batching — handled. Agents that try to roll their own usually get one of those wrong.

3. **Visual self-verification baked into the workflow.** The skill explicitly tells Claude to `Read` the generated PNG and judge it against the prompt before showing the user. No more "here's an image, hope it's right!"

### Install

#### Claude Code (one-liner)

```bash
git clone https://github.com/jiangmuran/claude-image.git ~/.claude/skills/gpt-image-2 \
  && bash ~/.claude/skills/gpt-image-2/install.sh
```

The installer asks for your API key, writes it to `~/.zshrc`, and offers a smoke test.

After install, Claude auto-discovers the skill on the next image request — no restart, no registration.

#### Codex (or any agent that scans `~/.agents/skills/`)

```bash
git clone https://github.com/jiangmuran/claude-image.git ~/.agents/skills/gpt-image-2 \
  && bash ~/.agents/skills/gpt-image-2/install.sh
```

Same skill, same script, same env vars.

#### Manual / other agents / direct CLI use

```bash
git clone https://github.com/jiangmuran/claude-image.git
cd gpt-image-2

echo 'export OPENAI_IMAGE_API_KEY="sk-..."' >> ~/.zshrc
echo 'export OPENAI_IMAGE_BASE_URL="https://jmrai.net/v1"' >> ~/.zshrc
source ~/.zshrc

python3 scripts/gpt_image.py generate \
  -p "a red panda eating bamboo, flat vector illustration, off-white background" \
  -o ./test.png
open test.png
```

### Credentials

Two environment variables. That's the entire config surface.

| Var | Required | Default |
|-----|----------|---------|
| `OPENAI_IMAGE_API_KEY` | yes | — |
| `OPENAI_IMAGE_BASE_URL` | no | `https://jmrai.net/v1` |

Falls back to `OPENAI_API_KEY` / `OPENAI_BASE_URL` if the image-specific ones aren't set.

**Buy credits:** https://order.jmrai.net

> **Don't commit your key.** `.gitignore` excludes `.env`. The `.env.example` is a template only.

### What it can do

A non-exhaustive sample (full catalog in `references/use-cases.md`):

- **Pitch-deck slides** — looks like a real Series A board slide. Specific data, specific fonts, specific palettes. Multi-slide consistency via the edit endpoint.
- **Chinese posters & signage** — quoted text + script flavor (`楷书 / 黑体 / 思源黑体`) + "no extra Chinese characters" tail. Renders crisply.
- **Realistic UI mockups** — desktop dashboards, mobile screens, in real device frames with believable copy.
- **Pixel art & game assets** — character sprites, top-down tilesets (chroma-key magenta backgrounds), item icons, character reference sheets with multiple views.
- **Infographics** — vertical info-dense diagrams that GPT Image 2 actually renders correctly.
- **Logo concepts** — 2x2 grids of variants exploring different shape languages. Vector-clean, no gradients, no 3D.
- **Photoreal product shots** — proper photo language (50mm f/2.8, north-window light, 35mm film grain) instead of "premium quality".
- **Surgical photo edits** — the `change ONLY X / preserve Y exactly` pattern.
- **Report figures & spot illustrations** — FT-style editorial diagrams, gouache section illustrations, app empty-state characters.

### How it teaches your agent to write prompts

The full guide is in `references/prompting.md`. Headline: **drop the magic words.**

Pre-GPT-Image-2 prompting:

```
beautiful stunning ultra-detailed 4K 8K masterpiece trending on artstation
cinematic lighting professional photography premium quality
```

GPT Image 2 doesn't reward this. It rewards instructional, specific, intent-first prompts. The skill teaches the canonical structure:

```
Intent  →  Scene  →  Subject  →  Details  →  Text  →  Style  →  Constraints
```

Plus the seven habits: **state intent first, quote every character, use spec-language not praise-language, "change ONLY X / preserve Y" for edits, one style anchor not five, drop the magic words, iterate-don't-stack**.

### Why visual self-verification matters

The skill tells Claude to **Read the generated PNG and judge it against the prompt** before showing the user. If anything fails, the agent iterates **one dimension at a time** and regenerates. The user sees the *good* result, not "here's what I got, does it look right?"

This works because Claude *can* see images. It just doesn't, by default, look at things it generates. The skill changes that default.

### Architecture

- **Zero Python deps.** Uses only `urllib`, `concurrent.futures`, `argparse`. Runs on any Python 3.7+.
- **Parallel batching.** `-n 4` fires four parallel single-image requests rather than asking the API for n=4. Faster wall-clock, works regardless of host n>1 support.
- **Sane defaults.** `--quality high` by default (cost is identical across quality tiers on this host). `--size 1024x1024`. `--concurrency 4`.
- **Upfront validation.** Resolution constraints (max side <3840px, ratio ≤3:1) checked before the API round-trip.
- **Multi-image input gracefully refused.** This host's gpt-image-2 doesn't accept multiple input images per /edits call.

### Manual usage

```bash
GI="python3 ~/.claude/skills/gpt-image-2/scripts/gpt_image.py"

$GI generate -p "a misty mountain temple at dawn, Studio Ghibli watercolor" -o ./temple.png
$GI generate -p "..." -n 4 --concurrency 4 -o ./out
$GI edit -i ./photo.png -p "Edit the input: replace ONLY the sky with northern lights. Preserve everything else exactly." -o ./aurora.png
$GI generate --help
$GI edit --help
```

### Updating

```bash
cd ~/.claude/skills/gpt-image-2 && git pull
```

The skill is text + a script. No build step, no restart, no registration.

### Customizing for your team

Fork it. Pieces designed to be swapped:

- **`references/use-cases.md`** — add your house style, brand palettes, recurring asset templates
- **`scripts/gpt_image.py`** — add a `--watermark` flag, custom output naming, S3 upload, etc.
- **`DEFAULT_BASE`** — point at your private gateway

Pull requests welcome if your additions are general-purpose.

### License

MIT. See `LICENSE`. Use it however.

### Credits

Built for [Claude Code](https://claude.com/claude-code) but the pattern (markdown skill + zero-dep CLI + visual self-verification) works with any agent that can read files and call a script.

Inspiration: OpenAI's official GPT Image 2 Cookbook, Anthropic's superpowers/writing-skills patterns for agent-discoverable skills.
