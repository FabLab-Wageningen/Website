#!/usr/bin/env python3
"""Build the FabLab Wageningen website.

Reads Markdown and YAML from content/, renders it with the templates in
templates/, copies static/ as-is, and writes the finished site to _site/.

Usage:
    python build.py          build the site into _site/
    python build.py serve    build, then preview at http://localhost:8000

The environment variable BASE_PATH is set by the GitHub workflow when the
site is served from a sub folder (for example /Website on github.io). With
our own domain it is empty and nothing changes.
"""

import datetime as dt
import os
import re
import shutil
import sys
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
OUT = ROOT / "_site"
LANGS = ("nl", "en")
BASE = os.environ.get("BASE_PATH", "").rstrip("/")

MD_EXTENSIONS = ["extra", "sane_lists"]  # "extra" adds tables and markdown inside <div markdown="1">

DAYS = {
    "nl": ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"],
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
}
MONTHS = {
    "nl": ["januari", "februari", "maart", "april", "mei", "juni", "juli",
           "augustus", "september", "oktober", "november", "december"],
    "en": ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"],
}


# ---------------------------------------------------------------- helpers

def read_markdown_file(path):
    """Split a file into (front matter dict, Markdown body)."""
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        _, front, body = text.split("---", 2)
        meta = yaml.safe_load(front) or {}
    else:
        meta, body = {}, text
    return meta, body.strip()


def md(text):
    return markdown.markdown(text or "", extensions=MD_EXTENSIONS)


def with_base(html):
    """Prefix site-internal links with BASE_PATH (only needed on github.io)."""
    if not BASE:
        return html
    html = re.sub(r'((?:href|src|content)=")/(?!/)', rf"\1{BASE}/", html)
    html = re.sub(r'(url=)/(?!/)', rf"\1{BASE}/", html)
    return re.sub(r"url\('/(?!/)", f"url('{BASE}/", html)


def write_page(url, html):
    """Write html so that `url` (e.g. /nl-page/) works on any static host."""
    if url == "/404.html":
        target = OUT / "404.html"
    else:
        target = OUT / url.strip("/") / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(with_base(html), encoding="utf-8")


def format_date(value, lang="nl", style="long"):
    d = value if isinstance(value, dt.date) else dt.date.fromisoformat(str(value))
    day, month = DAYS[lang][d.weekday()], MONTHS[lang][d.month - 1]
    if style == "short":
        return f"{d.day} {month}"
    return f"{day} {d.day} {month}"


def join_names(names, lang):
    names = [n for n in (names or []) if n]
    if len(names) <= 1:
        return "".join(names)
    word = "en" if lang == "nl" else "and"
    return ", ".join(names[:-1]) + f" {word} " + names[-1]


# ---------------------------------------------------------------- loading

def load_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_pages():
    pages = []
    for lang in LANGS:
        for path in sorted((CONTENT / "pages" / lang).glob("*.md")):
            meta, body = read_markdown_file(path)
            for field in ("title", "permalink", "key"):
                if field not in meta:
                    sys.exit(f"{path} is missing '{field}' in its front matter")
            meta["lang"] = lang
            meta.setdefault("template", "page.html")
            meta["content"] = md(body)
            pages.append(meta)
    return pages


def load_sessions(today):
    """Open workshop dates from content/data/open-inloop.yml."""
    sessions = []
    for item in load_yaml(CONTENT / "data" / "open-inloop.yml") or []:
        date = item["date"] if isinstance(item["date"], dt.date) else dt.date.fromisoformat(str(item["date"]))
        hosts = item.get("hosts") or []
        if isinstance(hosts, str):
            hosts = [hosts]
        sessions.append({
            "date": date,
            "start": str(item.get("start", "14:00")),
            "end": str(item.get("end", "17:00")),
            "hosts": hosts,
            "note": item.get("note", ""),
        })
    sessions.sort(key=lambda s: s["date"])
    return [s for s in sessions if s["date"] >= today], sessions


# ---------------------------------------------------------------- calendar

def ics_escape(text):
    return (str(text).replace("\\", "\\\\").replace(";", "\\;")
            .replace(",", "\\,").replace("\n", "\\n"))


def build_ics(site, sessions):
    """A calendar feed people can subscribe to (Outlook, Google, Apple)."""
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0",
        "PRODID:-//FabLab Wageningen//Open inloop//NL",
        "X-WR-CALNAME:FabLab Wageningen open inloop",
        "X-WR-TIMEZONE:Europe/Amsterdam",
    ]
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for s in sessions:
        day = s["date"].strftime("%Y%m%d")
        start, end = s["start"].replace(":", ""), s["end"].replace(":", "")
        hosts = join_names(s["hosts"], "nl")
        lines += [
            "BEGIN:VEVENT",
            f"UID:open-inloop-{day}@{site['domain']}",
            f"DTSTAMP:{stamp}",
            f"DTSTART;TZID=Europe/Amsterdam:{day}T{start}00",
            f"DTEND;TZID=Europe/Amsterdam:{day}T{end}00",
            "SUMMARY:FabLab Wageningen open inloop / open workshop",
            f"LOCATION:{ics_escape(site['address'])}",
            f"URL:{site['url']}/open-inloop/",
        ]
        description = " · ".join(x for x in (hosts, s["note"]) if x)
        if description:
            lines.append(f"DESCRIPTION:{ics_escape(description)}")
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    (OUT / "open-inloop.ics").write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")


# ---------------------------------------------------------------- build

def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(STATIC, OUT)

    env = Environment(loader=FileSystemLoader(TEMPLATES),
                      autoescape=select_autoescape(["html"]))
    env.filters["date"] = format_date
    env.filters["names"] = join_names
    env.filters["markdown"] = md

    site = load_yaml(CONTENT / "site.yml")
    machines = load_yaml(CONTENT / "data" / "machines.yml")
    today = dt.date.today()
    upcoming, all_sessions = load_sessions(today)
    pages = load_pages()

    # Which page is the translation of which: pages share a `key`.
    by_key = {}
    for p in pages:
        by_key.setdefault(p["key"], {})[p["lang"]] = p["permalink"]
    homes = {lang: by_key["home"][lang] for lang in LANGS}

    redirects = {}
    for page in pages:
        lang = page["lang"]
        translations = {l: by_key[page["key"]].get(l, homes[l]) for l in LANGS}
        html = env.get_template(page["template"]).render(
            page=page, site=site, t=site["text"][lang], lang=lang,
            nav=site["nav"][lang], translations=translations,
            machines=machines, upcoming=upcoming, today=today)
        write_page(page["permalink"], html)
        for alias in page.get("aliases", []):
            redirects[alias] = page["permalink"]

    redirect_tpl = env.get_template("redirect.html")
    for old, new in redirects.items():
        write_page(old, redirect_tpl.render(target=new))

    write_page("/404.html", env.get_template("404.html").render(
        page={"title": "Pagina niet gevonden / Page not found", "lang": "nl"},
        site=site, t=site["text"]["nl"], lang="nl", nav=site["nav"]["nl"],
        translations=homes))
    build_ics(site, all_sessions)

    print(f"Built {len(pages)} pages, {len(upcoming)} upcoming dates "
          f"and {len(redirects)} redirects into {OUT.name}/")


def serve():
    import functools
    import http.server
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    print("Preview at http://localhost:8000  (Ctrl+C to stop)")
    http.server.ThreadingHTTPServer(("localhost", 8000), handler).serve_forever()


if __name__ == "__main__":
    build()
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        serve()
