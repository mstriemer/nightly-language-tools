# Firefox Nightly Langpacks JSON

A static JSON file that mimics the [Mozilla Addons API](https://addons-server.readthedocs.io/en/latest/topics/api/addons.html#language-tools) `/api/v4/addons/language-tools/` endpoint for Firefox Nightly language packs.

The file is regenerated daily by a GitHub Actions workflow that scrapes Mozilla's public FTP server and committed to this repository, then served via GitHub Pages.

## Endpoint

```
https://mstriemer.github.io/nightly-language-tools/data/language-tools.json
```

## Usage

Firefox Nightly will access this API as needed if it's set up to do so. The relevant prefs are:

```
# Or your own local copy served with `python -m http.server` for example
extensions.getAddons.langpacks.url=https://mstriemer.github.io/nightly-language-tools/data/language-tools.json
intl.multilingual.enabled=true
intl.multilingual.downloadEnabled=true
# Optional
intl.multilingual.liveReload=true
intl.multilingual.liveReloadBidirectional=true
```

You could pass these to `mach` to set them quickly (only needed once):

```
./mach run --setpref extensions.getAddons.langpacks.url=https://mstriemer.github.io/nightly-language-tools/data/language-tools.json --setpref intl.multilingual.enabled=true --setpref intl.multilingual.downloadEnabled=true --setpref intl.multilingual.liveReload=true --setpref intl.multilingual.liveReloadBidirectional=true
```

## Generating locally

Requires Python 3.8+ and `httpx`:

```bash
pip install httpx
python generate.py
```

Writes to `data/language-tools.json` by default.

Options:

| Flag           | Description                                                           |
| -------------- | --------------------------------------------------------------------- |
| `--out <path>` | Write to a custom path instead                                        |
| `--check`      | Dry run — exits 1 if the output would change, 0 if already up to date |

## GitHub Pages setup

1. Push this repository to GitHub.
2. Go to **Settings → Pages → Source** and select **Deploy from a branch** → `main` / `/ (root)`.
3. Trigger the **Update langpacks JSON** workflow manually (Actions tab) to populate the file before the first scheduled run.

The workflow runs daily at 10:00 UTC and commits `data/language-tools.json` only when the content changes.

## Data source

XPI files are fetched from Mozilla's public FTP server:

```
https://ftp.mozilla.org/pub/firefox/nightly/latest-mozilla-central-l10n/linux-x86_64/xpi/
```
