<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=" align="left" width="120" height="120"/>

# Dex-Starr

> With test and code of crimson red,
> Ripped from a program so freshly dead,
> Together with our comics collate,
> We'll sort you all, that is your Fate!

[![PyPI - Python](https://img.shields.io/pypi/pyversions/Dex-Starr.svg?logo=Python&label=Python&style=flat-square)](https://pypi.python.org/pypi/Dex-Starr/)
[![PyPI - Status](https://img.shields.io/pypi/status/Dex-Starr.svg?logo=PyPI&label=Status&style=flat-square)](https://pypi.python.org/pypi/Dex-Starr/)
[![PyPI - Version](https://img.shields.io/pypi/v/Dex-Starr.svg?logo=PyPI&label=Version&style=flat-square)](https://pypi.python.org/pypi/Dex-Starr/)
[![PyPI - License](https://img.shields.io/pypi/l/Dex-Starr.svg?logo=PyPI&label=License&style=flat-square)](https://opensource.org/licenses/MIT)

[![Github - Contributors](https://img.shields.io/github/contributors/Buried-In-Code/Dex-Starr.svg?logo=Github&label=Contributors&style=flat-square)](https://github.com/Buried-In-Code/Dex-Starr/graphs/contributors)
[![Github Action - Code Analysis](https://img.shields.io/github/workflow/status/Buried-In-Code/Dex-Starr/Code-Analysis?logo=Github-Actions&label=Code-Analysis&style=flat-square)](https://github.com/Buried-In-Code/Dex-Starr/actions/workflows/code-analysis.yaml)
[![Github Action - Testing](https://img.shields.io/github/workflow/status/Buried-In-Code/Dex-Starr/Testing?logo=Github-Actions&label=Tests&style=flat-square)](https://github.com/Buried-In-Code/Dex-Starr/actions/workflows/testing.yaml)

[![Code Style - Black](https://img.shields.io/badge/Code%20Style-Black-000000.svg?style=flat-square)](https://github.com/psf/black)

Dex-Starr helps sort and organize your comic collection by using the information stored in ComicInfo files.
It also formats all your digital comics into a single format (CBZ) and transforms the `ComicInfo.xml` inside most digital comic files into `ComicInfo.json` using the below schema.
Dex-Starr can also fill in any blanks in the ComicInfo by pulling from a list of supported sources.

## Arguments

| Argument | Type | Required | Default | Notes |
| -------- | ---- | -------- | ------- | ----- |
| `--pull-info` | bool | False | False | Pull info and updates ComicInfo from available sources |
| `--show-variants` | bool | False | False | Add variants to the list of options |
| `--add-manual-info` | bool | False | False | Manually enter the data for the ComicInfo |
| `--manual-image-check` | bool | False | False | Pause the Script before creating the CBZ to allow manual removal of Ads, etc... |
| `--reset-info` | bool | False | False | Wipe all non-essential fields (fields used in searching e.g. title, issue #...) and lookup the info fresh |
| `--debug` | bool | False | False | |

## Execution

All settings can be found in `~/.dex-starr/settings.ini`
**Requires restart for changes to take effect**

### From PyPI
1. Run: `pip install Dex-Starr`
2. Run: `Dex-Starr`

### From Source
1. Make sure you have [Poetry](https://python-poetry.org) installed
2. Clone the repo: `git clone https://github.com/Buried-In-Code/Dex-Starr`
3. Navigate to the folder: `cd Dex-Starr/`
4. Run: `poetry install`
5. Run: `poetry run python -m DexStarr`

## Supported Sources:

- [Comicvine](https://comicvine.gamespot.com/api/)
- [Metron](https://metron.cloud/)
- [League of Comic Geeks](https://leagueofcomicgeeks.com/)
- ComicInfo File
- User Input

## Supported File Formats:

- `.ace`/`.cba`
- `.rar`/`.cbr`
- `.7z`/`.cb7`
- `.tar`/`.cbt`
- `.zip`/`.cbz`

## Supported Comic Formats:

- Comic
- Annual
- Digital Chapter
- Trade Paperback
- Hardcover

## Comic Collection Folder Structure

Root folder location is defined in `~/.dex-starr/settings.ini`

```
Root Folder
+-- Collection
|  +-- Publisher
|  |  +-- Series
|  |  |  +-- Comic.cbz
|  |  |  +-- Comic.cbz
|  |  +-- Series
|  |  |  +-- Comic.cbz
|  |  |  +-- Comic.cbz
|  +-- Publisher
|  |  +-- Series
|  |  |  +-- Comic.cbz
|  |  |  +-- Comic.cbz
|  |  +-- Series
|  |  |  +-- Comic.cbz
|  |  |  +-- Comic.cbz
+-- Import
|  +-- New-Comic.cbr
+-- Processing
```

## ComicInfo Json Schema

```
{
    "Series": {
        "Publisher": {
            "Title": <String>,
            "Identifiers": {
                "<Website>": {
                    "Id": <String|null>,
                    "Url": <String|null>
                }
            }
        },
        "Start Year": <Integer>,
        "Title": <String>,
        "Volume": <Integer|1>,
        "Identifiers": {
            "<Website>": {
                "Id": <String|null>,
                "Url": <String|null>
            }
        }
    },
    "Issue": {
        "Number": <String|1>,
        "Title": <String|null>
    },
    "Cover Date": <Date|yyyy-mm-dd|null>,
    "Store Date": <Date|yyyy-mm-dd|null>,
    "Format": <String|Comic>,
    "Language ISO": <String|EN>,
    "Page Count": <Integer|1>,
    "Summary": <String|null>,
    "Variant": <Boolean>,
    "Identifiers": {
        "<Website>": {
            "Id": <String|null>,
            "Url": <String|null>
        }
    },
    "Notes": <String|null>
}
```

## Socials

[![Social - Discord](https://img.shields.io/discord/618581423070117932.svg?logo=Discord&label=The-DEV-Environment&style=flat-square&colorB=7289da)](https://discord.gg/nqGMeGg)