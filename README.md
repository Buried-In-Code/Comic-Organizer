# Comic Organizer

[![Version](https://img.shields.io/github/tag-pre/Buried-In-Code/Comic-Organizer.svg?label=version&style=flat-square)](https://github.com/Buried-In-Code/Comic-Organizer/releases)
[![Issues](https://img.shields.io/github/issues/Buried-In-Code/Comic-Organizer.svg?style=flat-square)](https://github.com/Buried-In-Code/Comic-Organizer/issues)
[![Contributors](https://img.shields.io/github/contributors/Buried-In-Code/Comic-Organizer.svg?style=flat-square)](https://github.com/Buried-In-Code/Comic-Organizer/graphs/contributors)
[![License](https://img.shields.io/github/license/Buried-In-Code/Comic-Organizer.svg?style=flat-square)](https://opensource.org/licenses/MIT)

[![Code Analysis](https://img.shields.io/github/workflow/status/Buried-In-Code/Comic-Organizer/Code-Analysis?label=Code-Analysis&logo=github&style=flat-square)](https://github.com/Buried-In-Code/Comic-Organizer/actions/workflows/code-analysis.yml)

Comic-Organizer helps sort and organize your comic collection by using the information stored in ComicInfo files. It also formats all your digital comics into a single format (CBZ)
and transforms the `ComicInfo.xml` inside most digital comic files into `ComicInfo.json` using the below schema. Comic-Organizer can also fill in any blanks in the ComicInfo by
pulling from a list of supported sources.

Supported Comic Formats:

- `.ace`/`.cba`
- `.rar`/`.cbr`
- `.7z`/`.cb7`
- `.tar`/`.cbt`
- `.zip`/`.cbz`

Supported Comic Sources:

- [Comicvine](https://comicvine.gamespot.com/api/)
- [Metron](https://metron.cloud/)
- [League of Comic Geeks](https://leagueofcomicgeeks.com/)
- ComicInfo
- User Input

## Built Using

- [Poetry: 1.1.7](https://python-poetry.org)
- [Python: 3.9.6](https://www.python.org/)
- [Painted-Logger: 1.1.1](https://pypi.org/project/Painted-Logger)
- [ruamel.yaml: 0.17.10](https://pypi.org/project/ruamel.yaml)
- [titlecase: 2.3](https://pypi.org/project/titlecase)
- [requests: 2.26.0](https://pypi.org/project/requests)
- [beautifulsoup4: 4.9.3](https://pypi.org/project/beautifulsoup4)
- [lxml: 4.6.3](https://pypi.org/project/lxml)
- [patool: 1.12](https://pypi.org/project/patool)
- [colorama: 0.4.4](https://pypi.org/project/colorama)
- [mokkari: 0.2.2](https://pypi.org/project/mokkari)
- [simyan: 0.3.0](https://pypi.org/project/simyan)

## Arguments

| Argument | Type | Required | Default | Notes |
| -------- | ---- | -------- | ------- | ----- |
| `--input-folder` | str | True | | Path to folder to import the comic files. *Recursively navigates folder* |
| `--pull-info` | bool | False | False | Pull info and updates ComicInfo from available sources |
| `--show-variants` | bool | False | False | Add variants to the list of options |
| `--add-manual-info` | bool | False | False | Manually enter the data for the ComicInfo |
| `--manual-image-check` | bool | False | False | Pause the Script before creating the CBZ to allow manual removal of Ads, etc... |
| `--reset-info` | bool | False | False | Wipe all non-essential fields (fields used in searching e.g. title, issue #...) and lookup the info fresh |
| `--debug` | bool | False | False | |

## Execution

1. Make sure you have [Poetry](https://python-poetry.org) installed
2. Rename **config-example.ini** to **config.ini**
3. Fill out **config.ini**
4. Run: `poetry run python -m Organizer --input-folder "<path>"`

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
    "Creators": {
        "<Role>": [
            <String>
        ]
    },
    "Format": <String|Comic>,
    "Genres": [
        <String>
    ],
    "Language ISO": <String|EN>,
    "Page Count": <Integer|1>,
    "Summary": <String|null>,
    "Variant": <String|null>,
    "Identifiers": {
        "<Website>": {
            "Id": <String|null>,
            "Url": <String|null>
        }
    },
    "Notes": <String|null>
}
```

Common Formats:

- Comic
- Annual
- Digital Chapter
- Trade Paperback
- Hardcover

## Socials

[![Discord | The-DEV-Environment](https://discordapp.com/api/guilds/618581423070117932/widget.png?style=banner2)](https://discord.gg/nqGMeGg)