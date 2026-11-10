#!/usr/bin/env python3
"""Render the static, dark SVG cards used by the GitHub profile README."""
from __future__ import annotations

import argparse
import html
from pathlib import Path

BG = "#0d1117"
SURFACE = "#161b22"
SURFACE_ALT = "#1c2128"
TEXT = "#e6edf3"
MUTED = "#8b949e"
BORDER = "#30363d"
BLUE = "#58a6ff"
AMBER = "#e3b341"
RED = "#f47067"


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def svg_start(width: int, height: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{esc(title)}</title>',
        '<desc id="desc">Dark GitHub profile card with subtle accent styling.</desc>',
        '<style>',
        "text{font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}",
        "@keyframes rise{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}",
        "@keyframes pulse{0%,100%{opacity:.58}50%{opacity:1}}",
        ".enter{animation:rise .55s ease-out both}.accent{animation:pulse 4.8s ease-in-out infinite}",
        "@media(prefers-reduced-motion:reduce){*,.enter,.accent{animation:none!important}}",
        '</style>',
        f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="16" fill="{BG}" stroke="{BORDER}"/>',
    ]


def write_svg(out: Path, filename: str, lines: list[str]) -> None:
    lines.append('</svg>')
    (out / filename).write_text('\n'.join(lines) + '\n', encoding='utf-8')


def write_hero(out: Path) -> None:
    s = svg_start(1100, 230, "Harsh Tiwari — profile")
    s += [
        f'<rect x="1" y="1" width="1098" height="228" rx="16" fill="{SURFACE}"/>',
        f'<rect x="32" y="34" width="3" height="160" rx="2" fill="{BLUE}"/>',
        f'<text x="58" y="82" fill="{TEXT}" font-size="42" font-weight="650" class="enter">Harsh Tiwari</text>',
        f'<text x="60" y="119" fill="{MUTED}" font-size="17" class="enter" style="animation-delay:.08s">I build practical software across infrastructure and security.</text>',
        f'<text x="60" y="165" fill="{TEXT}" font-size="12" font-weight="650" letter-spacing="2">AREAS OF INTEREST</text>',
        f'<text x="60" y="190" fill="{MUTED}" font-size="15">Backend systems  ·  DevOps  ·  Applied AI  ·  Application security</text>',
        f'<circle cx="1032" cy="50" r="4" fill="{BLUE}" class="accent"/>',
    ]
    write_svg(out, "hero.svg", s)


def write_focus(out: Path, filename: str, label: str, detail: str, accent: str, delay: str) -> None:
    s = svg_start(350, 112, label)
    s += [
        f'<rect x="1" y="1" width="348" height="110" rx="15" fill="{SURFACE}"/>',
        f'<rect x="20" y="22" width="3" height="68" rx="2" fill="{accent}"/>',
        f'<text x="38" y="49" fill="{accent}" font-size="12" font-weight="700" letter-spacing="2" class="enter" style="animation-delay:{delay}">{label}</text>',
        f'<text x="38" y="73" fill="{TEXT}" font-size="13" class="enter" style="animation-delay:{delay}">{esc(detail)}</text>',
        f'<circle cx="322" cy="28" r="3" fill="{accent}" class="accent"/>',
    ]
    write_svg(out, filename, s)


def write_project(out: Path, filename: str, title: str, description: str, index: str, accent: str, delay: str) -> None:
    s = svg_start(520, 156, title)
    s += [
        f'<rect x="1" y="1" width="518" height="154" rx="15" fill="{SURFACE}"/>',
        f'<text x="24" y="32" fill="{accent}" font-size="11" font-weight="650" letter-spacing="1.7" class="enter" style="animation-delay:{delay}">FEATURED PROJECT  /  {index}</text>',
        f'<text x="24" y="74" fill="{TEXT}" font-size="25" font-weight="620" class="enter" style="animation-delay:{delay}">{esc(title)}</text>',
        f'<text x="24" y="105" fill="{MUTED}" font-size="13" class="enter" style="animation-delay:{delay}">{esc(description)}</text>',
        f'<text x="24" y="132" fill="{accent}" font-size="12">VIEW PROJECT  ↗</text>',
    ]
    write_svg(out, filename, s)


def write_experience(out: Path) -> None:
    s = svg_start(1100, 126, "Daikin internship experience")
    s += [
        f'<rect x="1" y="1" width="1098" height="124" rx="15" fill="{SURFACE}"/>',
        f'<text x="26" y="36" fill="{BLUE}" font-size="11" font-weight="650" letter-spacing="1.7">EXPERIENCE</text>',
        f'<text x="26" y="70" fill="{TEXT}" font-size="21" font-weight="620">Daikin</text>',
        f'<text x="26" y="97" fill="{MUTED}" font-size="14">SDE Intern  ·  June 2026 – August 2026</text>',
        f'<line x1="460" y1="25" x2="460" y2="101" stroke="{BORDER}"/>',
        f'<text x="488" y="51" fill="{TEXT}" font-size="14">Security automation, local AI systems, and Android app auditing.</text>',
        f'<text x="488" y="77" fill="{MUTED}" font-size="13">SOAR alert triage  ·  Ollama / Llama 3 with Redis  ·  Python security tooling</text>',
    ]
    write_svg(out, "experience.svg", s)


def write_highlights(out: Path) -> None:
    s = svg_start(1100, 126, "Selected achievements")
    s += [
        f'<rect x="1" y="1" width="1098" height="124" rx="15" fill="{SURFACE}"/>',
        f'<text x="26" y="36" fill="{AMBER}" font-size="11" font-weight="650" letter-spacing="1.7">HIGHLIGHTS</text>',
        f'<text x="26" y="75" fill="{TEXT}" font-size="17" font-weight="600">Smart India Hackathon 2024</text>',
        f'<text x="26" y="99" fill="{MUTED}" font-size="13">Winner</text>',
        f'<line x1="540" y1="25" x2="540" y2="101" stroke="{BORDER}"/>',
        f'<text x="570" y="75" fill="{TEXT}" font-size="17" font-weight="600">Research published in IJACEN</text>',
        f'<text x="570" y="99" fill="{MUTED}" font-size="13">August 2025</text>',
    ]
    write_svg(out, "highlights.svg", s)


def render(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    write_hero(out)
    write_focus(out, "build.svg", "BUILD", "Backend systems and product engineering", BLUE, "0s")
    write_focus(out, "operate.svg", "OPERATE", "Linux, infrastructure, and automation", AMBER, ".08s")
    write_focus(out, "secure.svg", "SECURE", "Application security and resilience", RED, ".16s")
    write_project(out, "secure-evidence.svg", "Secure Evidence", "Evidence management with integrity, access control and auditability.", "01", BLUE, "0s")
    write_project(out, "apk-scanner.svg", "APK Scanner", "Android application analysis with automated security scanning.", "02", RED, ".1s")
    write_experience(out)
    write_highlights(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="dist/cards", help="Directory in which SVG cards are written")
    args = parser.parse_args()
    render(Path(args.output))
    print(f"Rendered 8 profile cards to {Path(args.output).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
