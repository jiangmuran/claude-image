#!/usr/bin/env python3
"""gpt_image.py — call the gpt-image-2 model via the OpenAI-compatible Images API.

Subcommands:
  generate   POST /images/generations
  edit       POST /images/edits  (single source image; optional mask for inpainting)

Reads OPENAI_IMAGE_API_KEY (required) and OPENAI_IMAGE_BASE_URL (default
https://jmrai.net/v1) from the environment. Falls back to OPENAI_API_KEY /
OPENAI_BASE_URL if the image-specific ones aren't set.

Behavior tuned for this host:
  * Quality is the same price across tiers, so default --quality high.
  * Multi-image *input* is NOT supported by this host's gpt-image-2.
    For composition, do it in two steps (generate base, then edit).
  * `-n N` fires N **parallel** single-image requests rather than asking the
    API for n=N in one call. Faster wall-clock and works regardless of whether
    the host supports n>1.

Outputs are written to disk and the absolute paths are printed, one per line,
on stdout — so callers can capture the paths cleanly.

No third-party dependencies; uses urllib only so it runs on any Python 3.7+.
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

DEFAULT_BASE = (
    os.environ.get("OPENAI_IMAGE_BASE_URL")
    or os.environ.get("OPENAI_BASE_URL")
    or "https://jmrai.net/v1"
)
DEFAULT_MODEL = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2")
DEFAULT_QUALITY = "high"   # this host charges the same across qualities
DEFAULT_CONCURRENCY = 4

# Constraints reported by the host's gpt-image-2.
MAX_SIDE = 3840
MAX_RATIO = 3.0  # long:short side


def _key() -> str:
    key = os.environ.get("OPENAI_IMAGE_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not key:
        sys.exit(
            "ERROR: set OPENAI_IMAGE_API_KEY (or OPENAI_API_KEY).\n"
            "  export OPENAI_IMAGE_API_KEY='sk-...'\n"
            "  export OPENAI_IMAGE_BASE_URL='https://jmrai.net/v1'   # optional"
        )
    return key


def _validate_size(size: str) -> None:
    try:
        w, h = (int(x) for x in size.lower().split("x", 1))
    except Exception:
        sys.exit(f"ERROR: --size must be WxH (got {size!r})")
    if w <= 0 or h <= 0:
        sys.exit(f"ERROR: --size dimensions must be positive (got {size!r})")
    if max(w, h) >= MAX_SIDE:
        sys.exit(
            f"ERROR: longest side must be < {MAX_SIDE}px "
            f"(got {max(w, h)}px in {size!r})"
        )
    ratio = max(w, h) / min(w, h)
    if ratio > MAX_RATIO:
        sys.exit(
            f"ERROR: aspect ratio must be ≤ {MAX_RATIO:.0f}:1 "
            f"(got {ratio:.2f}:1 in {size!r})"
        )


_print_lock = threading.Lock()


def _send(req: urllib.request.Request, retries: int = 4) -> dict:
    last_err: str | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            # Retry on 429 and 5xx, surface 4xx immediately
            if (e.code == 429 or 500 <= e.code < 600) and attempt < retries - 1:
                wait = 2 ** attempt + (0.1 * attempt)
                time.sleep(wait)
                last_err = f"HTTP {e.code}: {body}"
                continue
            sys.exit(f"HTTP {e.code} from {req.full_url}\n{body}")
        except urllib.error.URLError as e:
            last_err = f"network error: {e}"
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            sys.exit(last_err)
    sys.exit(last_err or "unknown error")


def _post_json(path: str, payload: dict) -> dict:
    url = DEFAULT_BASE.rstrip("/") + path
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {_key()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    return _send(req)


def _post_multipart(path: str, fields: dict, files: dict[str, list[str]]) -> dict:
    url = DEFAULT_BASE.rstrip("/") + path
    boundary = f"----gptimage{int(time.time() * 1000)}{threading.get_ident()}"
    parts: list[bytes] = []

    for k, v in fields.items():
        if v is None:
            continue
        parts.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{k}"\r\n\r\n'
            f"{v}\r\n".encode("utf-8")
        )

    for field_name, paths in files.items():
        for raw in paths:
            fp = Path(raw).expanduser()
            if not fp.exists():
                sys.exit(f"ERROR: file not found: {fp}")
            mime = mimetypes.guess_type(fp.name)[0] or "image/png"
            parts.append(
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="{field_name}"; '
                f'filename="{fp.name}"\r\n'
                f"Content-Type: {mime}\r\n\r\n".encode("utf-8")
            )
            parts.append(fp.read_bytes())
            parts.append(b"\r\n")

    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(parts)
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {_key()}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/json",
        },
        method="POST",
    )
    return _send(req)


def _download(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=300) as r:
        return r.read()


def _output_paths(out_arg: str | None, n: int) -> list[Path]:
    if out_arg is None:
        base = Path.cwd() / f"gpt-image-{int(time.time())}"
        ext = ".png"
    else:
        p = Path(out_arg).expanduser()
        if p.suffix == "" and ((p.exists() and p.is_dir()) or out_arg.endswith("/")):
            p.mkdir(parents=True, exist_ok=True)
            base = p / "image"
            ext = ".png"
        else:
            base = p.with_suffix("")
            ext = p.suffix or ".png"
            base.parent.mkdir(parents=True, exist_ok=True)

    return [
        Path(f"{base}{'' if n == 1 else f'-{i + 1}'}{ext}")
        for i in range(n)
    ]


def _write_item(item: dict, dest: Path) -> Path:
    if "b64_json" in item and item["b64_json"]:
        dest.write_bytes(base64.b64decode(item["b64_json"]))
    elif "url" in item and item["url"]:
        dest.write_bytes(_download(item["url"]))
    else:
        sys.exit(f"ERROR: response item missing b64_json/url: {item}")
    with _print_lock:
        print(dest.resolve(), flush=True)
    return dest.resolve()


def _run_parallel(
    n: int,
    concurrency: int,
    fn,                 # callable that returns a dict (single API response)
    paths: list[Path],
) -> list[Path]:
    """Fire `n` calls in parallel and write each response to paths[i]."""
    results: list[Path | None] = [None] * n
    workers = max(1, min(concurrency, n))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(fn): i for i in range(n)}
        for fut in as_completed(futures):
            i = futures[fut]
            data = fut.result()
            items = data.get("data") or []
            if not items:
                sys.exit(f"ERROR: empty response: {json.dumps(data)[:500]}")
            results[i] = _write_item(items[0], paths[i])
    return [r for r in results if r is not None]


def cmd_generate(a: argparse.Namespace) -> None:
    _validate_size(a.size)
    payload = {
        "model": a.model,
        "prompt": a.prompt,
        "n": 1,
        "size": a.size,
    }
    if a.quality:
        payload["quality"] = a.quality
    if a.style:
        payload["style"] = a.style
    if a.background:
        payload["background"] = a.background
    if a.format:
        payload["response_format"] = a.format
    if a.user:
        payload["user"] = a.user

    paths = _output_paths(a.out, a.n)

    if a.n == 1:
        data = _post_json("/images/generations", payload)
        items = data.get("data") or []
        if not items:
            sys.exit(f"ERROR: empty response: {json.dumps(data)[:500]}")
        _write_item(items[0], paths[0])
        return

    _run_parallel(
        n=a.n,
        concurrency=a.concurrency,
        fn=lambda: _post_json("/images/generations", payload),
        paths=paths,
    )


def cmd_edit(a: argparse.Namespace) -> None:
    _validate_size(a.size)
    if len(a.image) > 1:
        sys.exit(
            "ERROR: this host's gpt-image-2 does not accept multiple input images.\n"
            "Workflow for compositions: generate or edit a base, then edit again "
            "with the next layer described in the prompt."
        )

    fields = {
        "model": a.model,
        "prompt": a.prompt,
        "n": "1",
        "size": a.size,
    }
    if a.quality:
        fields["quality"] = a.quality
    if a.background:
        fields["background"] = a.background
    if a.format:
        fields["response_format"] = a.format
    if a.user:
        fields["user"] = a.user
    files: dict[str, list[str]] = {"image": list(a.image)}
    if a.mask:
        files["mask"] = [a.mask]

    paths = _output_paths(a.out, a.n)

    def _call() -> dict:
        return _post_multipart("/images/edits", fields, files)

    if a.n == 1:
        data = _call()
        items = data.get("data") or []
        if not items:
            sys.exit(f"ERROR: empty response: {json.dumps(data)[:500]}")
        _write_item(items[0], paths[0])
        return

    _run_parallel(n=a.n, concurrency=a.concurrency, fn=_call, paths=paths)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Call gpt-image-2 over the OpenAI-compatible Images API.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Notes for this host (jmrai.net default):\n"
            "  * Quality is the same price across tiers — default is 'high'.\n"
            "  * `-n N` fires N parallel single-image calls.\n"
            "  * Multi-image *input* (compose 2 sources in one /edits call) is not supported.\n"
            "  * Max side < 3840px, aspect ratio ≤ 3:1.\n"
        ),
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    common_quality = dict(
        choices=["low", "medium", "high", "standard", "hd"],
        default=DEFAULT_QUALITY,
        help=f"rendering quality (default {DEFAULT_QUALITY}; "
             "all tiers cost the same on this host)",
    )

    g = sub.add_parser("generate", aliases=["gen"], help="generate from a text prompt")
    g.add_argument("-p", "--prompt", required=True, help="text prompt")
    g.add_argument("--size", default="1024x1024",
                   help="WxH; max side <3840, ratio ≤3:1; "
                        "e.g. 1024x1024, 1536x1024, 1024x1536, 1536x864, 2048x2048")
    g.add_argument("-n", type=int, default=1,
                   help="number of images (fires N parallel calls; default 1)")
    g.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                   help=f"max parallel requests when n>1 (default {DEFAULT_CONCURRENCY})")
    g.add_argument("-o", "--out",
                   help="output file path or directory; auto-suffixed when n>1")
    g.add_argument("--model", default=DEFAULT_MODEL)
    g.add_argument("--quality", **common_quality)
    g.add_argument("--style", choices=["vivid", "natural"],
                   help="overall style hint if supported")
    g.add_argument("--background", choices=["transparent", "opaque", "auto"],
                   help="transparent for stickers/icons/sprites")
    g.add_argument("--format", choices=["url", "b64_json"],
                   help="response format hint (script handles either)")
    g.add_argument("--user", help="optional user identifier passed to the API")
    g.set_defaults(fn=cmd_generate)

    e = sub.add_parser("edit", help="edit / inpaint an existing image")
    e.add_argument("-i", "--image", action="append", required=True,
                   help="path to source image (host accepts only one — script errors on >1)")
    e.add_argument("-p", "--prompt", required=True,
                   help="describe ONLY the change you want")
    e.add_argument("--mask", help="optional PNG mask; white pixels = regenerate")
    e.add_argument("--size", default="1024x1024")
    e.add_argument("-n", type=int, default=1,
                   help="number of variants (fires N parallel calls; default 1)")
    e.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                   help=f"max parallel requests when n>1 (default {DEFAULT_CONCURRENCY})")
    e.add_argument("-o", "--out")
    e.add_argument("--model", default=DEFAULT_MODEL)
    e.add_argument("--quality", **common_quality)
    e.add_argument("--background", choices=["transparent", "opaque", "auto"])
    e.add_argument("--format", choices=["url", "b64_json"])
    e.add_argument("--user")
    e.set_defaults(fn=cmd_edit)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
