# Dex-Starr

> With test and code of crimson red,\
> Ripped from a program so freshly dead,\
> Together with our comics collate,\
> We'll sort you all, that is your Fate!

[![PyPI - Python](https://img.shields.io/pypi/pyversions/Dex-Starr.svg?logo=PyPI&label=Python&style=flat-square)](https://pypi.python.org/pypi/Dex-Starr/)
[![PyPI - Status](https://img.shields.io/pypi/status/Dex-Starr.svg?logo=PyPI&label=Status&style=flat-square)](https://pypi.python.org/pypi/Dex-Starr/)
[![PyPI - Version](https://img.shields.io/pypi/v/Dex-Starr.svg?logo=PyPI&label=Version&style=flat-square)](https://pypi.python.org/pypi/Dex-Starr/)
[![PyPI - License](https://img.shields.io/pypi/l/Dex-Starr.svg?logo=PyPI&label=License&style=flat-square)](https://opensource.org/licenses/GPL-3.0)

[![Pre-Commit](https://img.shields.io/badge/Pre--Commit-Enabled-informational?logo=pre-commit&style=flat-square)](https://github.com/pre-commit/pre-commit)
[![Black](https://img.shields.io/badge/Black-Enabled-000000?style=flat-square)](https://github.com/psf/black)
[![isort](https://img.shields.io/badge/Imports-isort-informational?style=flat-square)](https://pycqa.github.io/isort/)
[![Flake8](https://img.shields.io/badge/Flake8-Enabled-informational?style=flat-square)](https://github.com/PyCQA/flake8)

[![Github - Contributors](https://img.shields.io/github/contributors/Buried-In-Code/Dex-Starr.svg?logo=Github&label=Contributors&style=flat-square)](https://github.com/Buried-In-Code/Dex-Starr/graphs/contributors)

[![Github Action - Code Analysis](https://img.shields.io/github/workflow/status/Buried-In-Code/Dex-Starr/Code%20Analysis?logo=Github-Actions&label=Code-Analysis&style=flat-square)](https://github.com/Buried-In-Code/Dex-Starr/actions/workflows/code-analysis.yaml)
[![Github Action - Testing](https://img.shields.io/github/workflow/status/Buried-In-Code/Dex-Starr/Testing?logo=Github-Actions&label=Tests&style=flat-square)](https://github.com/Buried-In-Code/Dex-Starr/actions/workflows/testing.yaml)

Dex-Starr helps sort and organize your comic collection by using the information stored in ComicInfo files.\
It also formats all your digital comics into a single format (cbz or cb7), adds and/or updates the supported list of Info files.\
Dex-Starr can also pull information from a list of sources to populate missing fields.

## Supported Formats

### Input Extensions

- .cbz
- .cbr
- .cbt
- .cb7

### Output Extensions

- .cbz
- .cb7

### Info Files

- Metadata.json
- [MetronInfo.xml](https://github.com/Metron-Project/metroninfo)
- [ComicInfo.xml](https://github.com/anansi-project/comicinfo)

## Installation/Execution

1. Make sure you have [Python](https://www.python.org/) installed: `python --version`
2. Make sure you have [Poetry](https://python-poetry.org) installed: `poetry --version`
3. Clone this repo: `git clone https://github.com/Buried-In-Code/Dex-Starr`
4. Install the project and its dependencies via poetry: `poetry install`
5. Run the program: `poetry run Dex-Starr`

### Arguments

| Argument             | Type | Description                                                                       |
| -------------------- | ---- | --------------------------------------------------------------------------------- |
| `import_folder`      | str  | Folder for Comics to be imported and parsed by Dex-Starr                          |
| `--manual-edit`      | bool | Pause the Script before bundling the files to allow manual removal of Ads, etc... |
| `--resolve-manually` | bool | Manually choose which fields are chosen by the importer                           |

## Services

- [Comicvine](https://comicvine.gamespot.com) using [Simyan](https://github.com/Metron-Project/Simyan)
- [League of Comic Geeks](https://leagueofcomicgeeks.com) using [Himon](https://github.com/Buried-In-Code/Himon)
- [Marvel](https://www.marvel.com/comics) using [Esak](https://github.com/Metron-Project/Esak)
- [Metron](https://metron.cloud) using [Mokkari](https://github.com/Metron-Project/Mokkari)

## File Renaming

### Series Naming

Series with volume greater than 1 will display its volume in the title.

### Comic Naming

The files are named based on the format of Comic:

- **_Default_**: `{Series Title}-#{Issue Number}.cbz`
- Annual: `{Series Title}-Annual-#{Issue Number}.cbz`
- Digital Chapter: `{Series Title}-Chapter-#{Issue Number}.cbz`
- Hardcover *(If it is a numbered issue)*: `{Series Title}-#{Issue Number}-HC.cbz`
- Hardcover *(If it is not a numbered issue)*: `{Series Title}-{Issue Title}-HC.cbz`
- Trade Paperback *(If it is a numbered issue)*: `{Series Title}-#{Issue Number}-TP.cbz`
- Trade Paperback *(If it is not a numbered issue)*: `{Series Title}-{Issue Title}-TP.cbz`

## Collection Folder Structure

```
Root Folder
+-- Import
|  +-- New Comic #10.cbr
|  +-- New Comic #11.cbz
+-- Processing
+-- Collection
|  +-- Publisher
|  |  +-- Series
|  |  |  +-- Series-#1.cbz
|  |  |  +-- Series-Annual-#1.cbz
|  |  |  +-- Series-Chapter-#1.cbz
|  |  |  +-- Series-#1-HC.cbz
|  |  |  +-- Series-Title-HC.cbz
|  |  |  +-- Series-#1-TP.cbz
|  |  |  +-- Series-Title-TP.cbz
|  |  +-- Series-v2
|  |  |  +-- Series-v2-#1.cbz
|  |  |  +-- Series-v2-Annual-#1.cbz
|  |  |  +-- Series-v2-Chapter-#1.cbz
|  |  |  +-- Series-v2-#1-HC.cbz
|  |  |  +-- Series-v2-Title-HC.cbz
|  |  |  +-- Series-v2-#1-TP.cbz
|  |  |  +-- Series-v2-Title-TP.cbz
```

## Socials

[![Social - Discord](https://img.shields.io/badge/Discord-The--DEV--Environment-7289DA?logo=Discord&style=flat-square)](https://discord.gg/nqGMeGg)
