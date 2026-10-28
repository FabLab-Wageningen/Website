# FabLab Wageningen website

The website of FabLab Wageningen, <https://fablabwag.nl>, in Dutch and English.

All content is plain text: Markdown for pages, YAML for lists (open inloop dates, the machine tiles, the menus). A small Python script (`build.py`) turns it into a static website. Editing the site means editing a text file; GitHub builds and publishes it automatically whenever something changes.

## Where things are

```
content/
  site.yml                 site name, menus (NL and EN), footer, fixed texts
  pages/nl/                one Markdown file per Dutch page
  pages/en/                one Markdown file per English page
  data/open-inloop.yml     the open inloop dates
  data/machines.yml        the coloured tiles on the homepage
static/
  css/style.css            colours, fonts, layout
  js/site.js               mobile menu and hiding past dates
  fonts/                   the Dosis font, served from this site
  wp-content/uploads/      images (same addresses as on the old WordPress site)
templates/                 HTML layout of each page type (rarely needs changing)
build.py                   the build script
requirements.txt           the Python packages the build uses, with exact versions
.github/workflows/         tells GitHub how to build and publish the site
```

## Common edits

You can do all of these directly on github.com: open the file, click the pencil icon, edit, and click "Commit changes". The live site updates about a minute later. The **Actions** tab shows whether the update worked (green tick) or not (red cross, with the reason).

### Add an open inloop date

Open `content/data/open-inloop.yml` and add a block:

```yaml
- date: 2027-01-16
  hosts:
    - Marcel vDijk
    - Tim
```

Only `date` is required. The time is 14:00-17:00 unless you add `start:` and `end:`. A short `note:` is shown under the date. Dates that have passed disappear from the site by themselves. The homepage shows the next four dates, the open inloop page shows all upcoming ones.

Each upcoming date has an "add to calendar" link to its own small calendar file (for example `/open-inloop/2027-01-16.ics`), which opens in Outlook, Google Calendar or Apple Calendar.

### Edit a page

Pages are in `content/pages/nl/` and `content/pages/en/`. Each file starts with a short header between two `---` lines:

```yaml
---
title: Lasersnijden          # shown as the page heading
permalink: /lasersnijden/    # the web address
key: laser                   # the same key in NL and EN links the two versions
aliases:                     # old addresses that should send people here
  - /fablab/lasersnijden/
---
```

Below the header is the page text in Markdown. Change the text, not the header, unless you mean to change the address. If you change a page in one language, check whether the other language needs the same change.

Two layouts use a little HTML around the Markdown; just edit the text between the tags:

- `<div class="media-text" markdown="1">` puts a photo next to the text (on phones the photo goes on top).
- `<div class="gallery" markdown="1">` shows the photos inside it in a row.

### Add a new page

Copy an existing page in the same folder, give the copy a new file name, and change `title`, `permalink` and `key`. Give the English version the same `key` so the language switch connects them. Add it to the menu in `content/site.yml` if it should appear there.

### Add or change an image

Upload the image to `static/wp-content/uploads/` (a sub folder like `2027/01/` is fine): open the folder on github.com, "Add file" then "Upload files". Then use it in a page:

```markdown
![Short description of the photo](/wp-content/uploads/2027/01/my-photo.jpg)
```

Keep photos around 1200 pixels wide or smaller, so pages load quickly.

### Change the menu or the homepage tiles

The menus for both languages are in `content/site.yml`. The tiles are in `content/data/machines.yml`, in the order they appear.

## Editing with Pages CMS

Besides editing on github.com, the site can be edited with [Pages CMS](https://pagescms.org), which shows forms instead of raw files. What it shows is set in `.pages.yml`:

- **Open inloop dates**: a form per Saturday (date, hosts, optional times and note).
- **Pages (Nederlands)** and **Pages (English)**: title, address, translation key and the page text in Markdown.
- **Homepage tiles**: icon, colour, titles and links.
- Images are uploaded to `static/wp-content/uploads/`.

People with access to this repository on GitHub sign in at app.pagescms.org with GitHub. Volunteers without a GitHub account can be invited by email for this repository only; they sign in with a code sent to that address and can edit content and images, not the settings. Every save is a commit and goes live about a minute later.

Pages CMS rewrites `content/data/open-inloop.yml` when it saves, so comments in that file disappear. That is expected.

## Markdown in short

```markdown
## A heading
Normal text. **Bold**, *italic*, [a link](/open-inloop/), <info@fablabwag.nl>.

- a list item
- another one

| Column | Column |
|---|---|
| a table | row |
```

A line break inside a paragraph needs two spaces at the end of the line.

## Publishing

The site is published by the workflow in `.github/workflows/deploy.yml` on every change to `main`. In the repository, **Settings → Pages** must have **Source: GitHub Actions**, the custom domain filled in, and **Enforce HTTPS** ticked. GitHub redirects between fablabwag.nl and www.fablabwag.nl by itself.

If the custom domain is ever removed, the site falls back to `https://fablab-wageningen.github.io/Website/`. Run the workflow again after any change to the custom domain (**Actions** → latest run → **Re-run all jobs**), so the links are built for the right address.

Old WordPress addresses keep working: they are listed under `aliases:` in the pages and send visitors to the new address.

## Preview on your own computer (optional)

You need Python 3.10 or newer.

```
pip install -r requirements.txt
python build.py serve
```

Then open <http://localhost:8000>. Press Ctrl+C to stop. Run it again after editing to see changes.

## Fonts

The site uses **Dosis** (`static/fonts/Dosis-latin.woff2`), served from this site so visitors' browsers don't contact Google. It is under the SIL Open Font License; see `static/fonts/LICENSE-Dosis.txt`.
