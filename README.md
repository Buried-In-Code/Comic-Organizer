# Comic Organizer

[![Version](https://img.shields.io/github/tag-pre/Buried-In-Code/Comic-Organizer.svg?label=version&style=flat-square)](https://github.com/Buried-In-Code/Comic-Organizer/releases)
[![Issues](https://img.shields.io/github/issues/Buried-In-Code/Comic-Organizer.svg?style=flat-square)](https://github.com/Buried-In-Code/Comic-Organizer/issues)
[![Contributors](https://img.shields.io/github/contributors/Buried-In-Code/Comic-Organizer.svg?style=flat-square)](https://github.com/Buried-In-Code/Comic-Organizer/graphs/contributors)
[![License](https://img.shields.io/github/license/Buried-In-Code/Comic-Organizer.svg?style=flat-square)](https://opensource.org/licenses/MIT)

[![Code Analysis](https://img.shields.io/github/workflow/status/Buried-In-Code/Comic-Organizer/Code-Analysis?label=Code-Analysis&logo=github&style=flat-square)](https://github.com/Buried-In-Code/Comic-Organizer/actions/workflows/code-analysis.yml)

*TODO*

## Built Using

- [Python: 3.9.6](https://www.python.org/)
- [pip: 21.1.3](https://pypi.org/project/pip/)
- [ruamel.yaml: 0.17.10](https://pypi.org/project/ruamel.yaml)
- [titlecase: 2.3](https://pypi.org/project/titlecase)
- [requests: 2.26.0](https://pypi.org/project/requests)
- [beautifulsoup4: 4.9.3](https://pypi.org/project/beautifulsoup4)
- [lxml: 4.6.3](https://pypi.org/project/lxml)
- [patool: 1.12](https://pypi.org/project/patool)

## Arguments

| Argument | Type | Required | Default | Notes |
| -------- | ---- | -------- | ------- | ----- |
| `--debug` | bool | False | False | |

## ComicInfo Json Schema

```
{
    "Publisher": <String>,
    "Series": {
        "Title": <String>,
        "Volume": <Integer|1>
    },
    "Comic": {
        "Number": <String|1>,
        "Title": <String|null>
    },
    "Variant": <String|null>,
    "Summary": <String|null>,
    "Cover Date": <Date|yyyy-mm-dd|null>,
    "Language": <String|EN>,
    "Format": <String|Comic>,
    "Genres": [
        <String>
    ],
    "Page Count": <Integer|1>,
    "Creators": {
        "<Role>": [
            <String>
        ]
    },
    "Alternative Series": [
        {
            "Title": <String>,
            "Volume": <Integer|1>,
            "Number": <String|1>
        }
    ],
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