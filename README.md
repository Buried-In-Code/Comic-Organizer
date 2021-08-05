# Comic Organizer

[![Version](https://img.shields.io/github/tag-pre/Buried-In-Code/Comic-Organizer.svg?label=version&style=flat-square)](https://github.com/Buried-In-Code/Comic-Organizer/releases)
[![Issues](https://img.shields.io/github/issues/Buried-In-Code/Comic-Organizer.svg?style=flat-square)](https://github.com/Buried-In-Code/Comic-Organizer/issues)
[![Contributors](https://img.shields.io/github/contributors/Buried-In-Code/Comic-Organizer.svg?style=flat-square)](https://github.com/Buried-In-Code/Comic-Organizer/graphs/contributors)
[![License](https://img.shields.io/github/license/Buried-In-Code/Comic-Organizer.svg?style=flat-square)](https://opensource.org/licenses/MIT)

[![Code Analysis](https://img.shields.io/github/workflow/status/Buried-In-Code/Comic-Organizer/Code-Analysis?label=Code-Analysis&logo=github&style=flat-square)](https://github.com/Buried-In-Code/Comic-Organizer/actions/workflows/code-analysis.yml)

*TODO*

## Built Using

- [Python: 3.9.6](https://www.python.org/)
- [pip: 21.2.2](https://pypi.org/project/pip/)
- [ruamel.yaml: 0.17.10](https://pypi.org/project/ruamel.yaml)
- [titlecase: 2.3](https://pypi.org/project/titlecase)
- [requests: 2.26.0](https://pypi.org/project/requests)
- [beautifulsoup4: 4.9.3](https://pypi.org/project/beautifulsoup4)
- [lxml: 4.6.3](https://pypi.org/project/lxml)
- [patool: 1.12](https://pypi.org/project/patool)

## Arguments

| Argument | Type | Required | Default | Notes |
| -------- | ---- | -------- | ------- | ----- |
| `--input-folder` | str | True | | Path to folder to import the comic files. *Recursively navigates folder* |
| `--pull-info` | bool | False | False | Pull info and updates ComicInfo from [Comicvine](), [League of Comic Geeks]() and [Metron]() |
| `--show-variants` | bool | False | False | Add variants to the list of options |
| `--add-manual-info` | bool | False | False | Manually enter the data for the ComicInfo |
| `--manual-image-check` | bool | False | False | Pause the Script before creating the CBZ to allow manual removal of Ads, etc... |
| `--debug` | bool | False | False | |

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

[![Discord | The DEV Environment](https://discordapp.com/api/guilds/618581423070117932/widget.png?style=banner2)](https://discord.gg/nqGMeGg)