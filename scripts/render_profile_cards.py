#!/usr/bin/env python3
"""Render GitHub profile SVG cards using the authenticated user's contribution calendar.

No third-party Python packages are required. The GitHub Actions workflow supplies
GITHUB_TOKEN and publishes the generated SVGs to the repository's `output` branch.
"""
from __future__ import annotations

import argparse
import calendar
import html
import json
import os
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

BLUE = "#2864dc"
INK = "#20242b"
MUTED = "#69717d"
PAPER = "#f7f6f2"
LINE = "#e3e1da"

PROJECTS = [
    {
        "file": "secure-evidence.svg",
        "number": "01",
        "name": "Secure Evidence",
        "description": "Evidence management with integrity, access control and auditability.",
        "stack": "Next.js  ·  Supabase  ·  MinIO  ·  SHA-256",
    },
    {
        "file": "apk-scanner.svg",
        "number": "02",
        "name": "APK Scanner",
        "description": "Android application analysis with automated security scanning.",
        "stack": "Python  ·  Django  ·  MobSF",
    },
]

QUERY = """query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
            weekday
          }
        }
      }
    }
  }
}"""


def fetch_contributions(username: str, token: str) -> dict:
    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=364)
    payload = {
        "query": QUERY,
        "variables": {
            "login": username,
            "from": f"{start.isoformat()}T00:00:00Z",
            "to": f"{today.isoformat()}T23:59:59Z",
        },
    }
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "github-profile-svg-renderer",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub GraphQL returned HTTP {exc.code}: {details}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach GitHub GraphQL: {exc}") from exc

    if result.get("errors"):
        raise RuntimeError("GitHub GraphQL error: " + json.dumps(result["errors"]))
    try:
        return result["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    except (KeyError, TypeError) as exc:
        raise RuntimeError("GitHub did not return a contribution calendar for this profile.") from exc


def all_days(calendar_data: dict) -> list[dict]:
    days = []
    for week in calendar_data.get("weeks", []):
        days.extend(week.get("contributionDays", []))
    return sorted(days, key=lambda item: item["date"])


def stats_for(days: list[dict]) -> dict:
    parsed = [
        {**item, "parsed_date": date.fromisoformat(item["date"]), "count": int(item["contributionCount"])}
        for item in days
    ]
    active = [item for item in parsed if item["count"] > 0]
    by_weekday = defaultdict(int)
    by_month = defaultdict(int)
    for item in parsed:
        by_weekday[item["parsed_date"].strftime("%A")] += item["count"]
        by_month[item["parsed_date"].strftime("%Y-%m")] += item["count"]

    longest = current = run = 0
    previous = None
    for item in parsed:
        if item["count"] > 0:
            if previous and item["parsed_date"] == previous + timedelta(days=1):
                run += 1
            else:
                run = 1
            longest = max(longest, run)
            previous = item["parsed_date"]
        else:
            run = 0
            previous = item["parsed_date"]

    today = datetime.now(timezone.utc).date()
    active_dates = {item["parsed_date"] for item in active}
    cursor = today if today in active_dates else today - timedelta(days=1)
    while cursor in active_dates:
        current += 1
        cursor -= timedelta(days=1)

    busiest = max(by_weekday, key=by_weekday.get) if by_weekday else "—"
    months = sorted(by_month.items())[-12:]
    return {
        "total": sum(item["count"] for item in parsed),
        "active_days": len(active),
        "current_streak": current,
        "longest_streak": longest,
        "busiest_day": busiest,
        "months": months,
        "days": parsed,
    }


def svg_start(width: int, height: int, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">'
        f'<title>{html.escape(title)}</title>'
    )


def shared_style() -> str:
    return f"""<style>
      text {{ font-family: Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif; }}
      .serif {{ font-family: Georgia, 'Times New Roman', serif; }}
      .ink {{ fill: {INK}; }} .muted {{ fill: {MUTED}; }} .blue {{ fill: {BLUE}; }}
      .card {{ fill: {PAPER}; stroke: {LINE}; stroke-width: 1; }}
      @keyframes rise {{ from {{ opacity: 0; transform: translateY(12px); }} to {{ opacity: 1; transform: translateY(0); }} }}
      @keyframes shine {{ 0%, 65% {{ transform: translateX(-120%); }} 85%, 100% {{ transform: translateX(120%); }} }}
      @keyframes pulse {{ 0%, 100% {{ opacity: .35; }} 50% {{ opacity: .9; }} }}
      .enter {{ animation: rise .8s cubic-bezier(.2,.7,.2,1) both; }}
      .shine {{ animation: shine 5s ease-in-out infinite; }}
      .pulse {{ animation: pulse 2.8s ease-in-out infinite; }}
      @media (prefers-reduced-motion: reduce) {{ *, .enter, .shine, .pulse {{ animation: none !important; }} }}
    </style>"""


def write_hero(out: Path, username: str) -> None:
    svg = [svg_start(1100, 270, "Harsh Tiwari profile introduction"), shared_style()]
    svg.append(f'<rect x="1" y="1" width="1098" height="268" rx="18" class="card"/>')
    svg.append('<text x="54" y="58" font-size="13" letter-spacing="3" class="muted">ENGINEERING / BUILDING / LEARNING</text>')
    svg.append('<text x="50" y="142" font-size="68" class="serif ink enter">Harsh Tiwari</text>')
    svg.append('<text x="54" y="184" font-size="20" class="ink enter" style="animation-delay:.12s">I build systems that solve real problems.</text>')
    svg.append('<text x="54" y="224" font-size="14" class="muted">Backend  ·  DevOps  ·  Applied AI  ·  Security</text>')
    svg.append('<rect x="850" y="48" width="190" height="170" rx="14" fill="#eef1f7" stroke="#d9deea"/>')
    svg.append('<text x="945" y="143" text-anchor="middle" font-size="64" class="serif blue">HT</text>')
    svg.append('<circle cx="1022" cy="62" r="5" fill="#2864dc" class="pulse"/>')
    svg.append(f'<text x="850" y="244" font-size="12" class="muted">@{html.escape(username)}</text>')
    svg.append('</svg>')
    (out / "hero.svg").write_text("\n".join(svg), encoding="utf-8")


def write_tile(out: Path, filename: str, number: str, heading: str, line1: str, line2: str, accent: str) -> None:
    svg = [svg_start(350, 178, heading), shared_style()]
    svg.append(f'<rect x="1" y="1" width="348" height="176" rx="15" class="card"/>')
    svg.append(f'<rect x="22" y="23" width="38" height="3" rx="2" fill="{accent}"/>')
    svg.append(f'<text x="22" y="57" font-size="12" letter-spacing="2" class="muted">{number} / PROFILE</text>')
    svg.append(f'<text x="22" y="104" font-size="31" class="serif ink enter">{html.escape(heading)}</text>')
    svg.append(f'<text x="22" y="135" font-size="13" class="muted">{html.escape(line1)}</text>')
    svg.append(f'<text x="22" y="156" font-size="13" class="muted">{html.escape(line2)}</text>')
    svg.append(f'<circle cx="318" cy="30" r="5" fill="{accent}" class="pulse"/>')
    svg.append('</svg>')
    (out / filename).write_text("\n".join(svg), encoding="utf-8")


def write_activity(out: Path, stats: dict) -> None:
    svg = [svg_start(1100, 390, "Monthly GitHub contributions and activity statistics"), shared_style()]
    svg.append('<rect x="1" y="1" width="1098" height="388" rx="18" class="card"/>')
    svg.append('<text x="38" y="49" font-size="13" letter-spacing="2" class="muted">GITHUB / LAST 12 MONTHS</text>')
    metrics = [
        (38, "CONTRIBUTIONS", f"{stats['total']:,}"),
        (300, "ACTIVE DAYS", f"{stats['active_days']:,}"),
        (545, "CURRENT STREAK", f"{stats['current_streak']} days"),
        (810, "LONGEST STREAK", f"{stats['longest_streak']} days"),
    ]
    for x, label, value in metrics:
        svg.append(f'<text x="{x}" y="88" font-size="11" letter-spacing="1.1" class="muted">{label}</text>')
        svg.append(f'<text x="{x}" y="126" font-size="27" class="serif ink">{html.escape(value)}</text>')
    svg.append(f'<text x="38" y="159" font-size="12" class="muted">Busiest weekday: <tspan fill="{BLUE}" font-weight="600">{html.escape(stats["busiest_day"])}</tspan></text>')
    svg.append(f'<line x1="38" y1="184" x2="1062" y2="184" stroke="{LINE}"/>')
    months = stats["months"]
    max_value = max((value for _, value in months), default=1) or 1
    chart_left, chart_top, chart_height, bar_w, gap = 50, 220, 112, 51, 31
    for index, (month, value) in enumerate(months):
        x = chart_left + index * (bar_w + gap)
        height = max(3, (value / max_value) * chart_height)
        y = chart_top + chart_height - height
        fill = BLUE if value == max_value and value > 0 else "#b8c9ef"
        svg.append(f'<rect x="{x}" y="{chart_top}" width="{bar_w}" height="{chart_height}" rx="5" fill="#eceef2"/>')
        svg.append(f'<rect x="{x}" y="{y:.1f}" width="{bar_w}" height="{height:.1f}" rx="5" fill="{fill}" class="enter" style="animation-delay:{index * .035:.2f}s"/>')
        label = datetime.strptime(month, "%Y-%m").strftime("%b")
        svg.append(f'<text x="{x + bar_w/2}" y="356" text-anchor="middle" font-size="12" class="muted">{label}</text>')
    svg.append('</svg>')
    (out / "activity.svg").write_text("\n".join(svg), encoding="utf-8")


def write_heatmap(out: Path, stats: dict) -> None:
    days = stats["days"]
    # GraphQL returns calendar weeks, but use date positions so the grid is stable.
    if not days:
        days = []
    first = date.fromisoformat(days[0]["date"]) if days else date.today()
    offset = (first.weekday() + 1) % 7  # Sunday-first, matching GitHub's calendar.
    columns = (len(days) + offset + 6) // 7
    cell, gap = 12, 5
    width = max(900, 72 + columns * (cell + gap) + 32)
    height = 180
    svg = [svg_start(width, height, "GitHub contribution heatmap"), shared_style()]
    svg.append(f'<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="18" class="card"/>')
    svg.append('<text x="28" y="34" font-size="13" letter-spacing="2" class="muted">CONTRIBUTION CALENDAR</text>')
    palette = ["#e9e8e2", "#d7e3fb", "#a9c4f3", "#6f99e8", BLUE]
    for index, item in enumerate(days):
        d = date.fromisoformat(item["date"])
        x_index = (offset + index) // 7
        y_index = (offset + index) % 7
        count = item["count"]
        level = 0 if count == 0 else 1 if count <= 2 else 2 if count <= 5 else 3 if count <= 9 else 4
        x = 28 + x_index * (cell + gap)
        y = 52 + y_index * (cell + gap)
        title = f"{d.isoformat()}: {count} contributions"
        svg.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{palette[level]}"><title>{html.escape(title)}</title></rect>')
    svg.append(f'<text x="28" y="164" font-size="11" class="muted">Less</text>')
    for i, color in enumerate(palette):
        svg.append(f'<rect x="67" y="153" width="12" height="12" rx="3" fill="{color}"/>')
        if i < 4:
            continue
    svg.append(f'<text x="158" y="164" font-size="11" class="muted">More</text>')
    svg.append('</svg>')
    (out / "heatmap.svg").write_text("\n".join(svg), encoding="utf-8")


def write_project(out: Path, project: dict) -> None:
    svg = [svg_start(520, 190, project["name"]), shared_style()]
    svg.append('<rect x="1" y="1" width="518" height="188" rx="16" class="card"/>')
    svg.append(f'<text x="28" y="36" font-size="12" letter-spacing="2" class="blue">PROJECT / {project["number"]}</text>')
    svg.append(f'<text x="28" y="83" font-size="31" class="serif ink">{html.escape(project["name"])}</text>')
    svg.append(f'<text x="28" y="116" font-size="13" class="muted">{html.escape(project["description"])}</text>')
    svg.append(f'<text x="28" y="158" font-size="12" class="muted">{html.escape(project["stack"])}</text>')
    svg.append('</svg>')
    (out / project["file"]).write_text("\n".join(svg), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="dist/cards", help="Directory in which SVG cards are written")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    username = os.environ.get("GITHUB_USERNAME", "Harsh-Tiwari678")
    if not token:
        print("GITHUB_TOKEN is required. In GitHub Actions, pass secrets.GITHUB_TOKEN.", file=sys.stderr)
        return 2

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    try:
        calendar_data = fetch_contributions(username, token)
        stats = stats_for(all_days(calendar_data))
        write_hero(output, username)
        write_tile(output, "build.svg", "01", "BUILD", "Backend systems and APIs", "Product engineering", BLUE)
        write_tile(output, "operate.svg", "02", "OPERATE", "Linux and infrastructure", "Automation and DevOps", "#8b6a39")
        write_tile(output, "secure.svg", "03", "SECURE", "Application security", "Privacy and resilience", "#b64e4e")
        write_activity(output, stats)
        write_heatmap(output, stats)
        for project in PROJECTS:
            write_project(output, project)
    except Exception as exc:  # Fail the workflow loudly rather than publish stale/empty graphics.
        print(f"Could not render profile cards: {exc}", file=sys.stderr)
        return 1

    print(f"Rendered profile cards to {output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
