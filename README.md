# Dex-Starr

> With test and code of crimson red,\
> Ripped from a program so freshly dead,\
> Together with our comics collate,\
> We'll sort you all, that is your Fate!

[![PyPI - Python](https://img.shields.io/pypi/pyversions/Dex-Starr.svg?logo=PyPI&label=Python&style=flat-square)](https://pypi.python.org/pypi/Dex-Starr/)
[![PyPI - Status](https://img.shields.io/pypi/status/Dex-Starr.svg?logo=PyPI&label=Status&style=flat-square)](https://pypi.python.org/pypi/Dex-Starr/)
[![PyPI - Version](https://img.shields.io/pypi/v/Dex-Starr.svg?logo=PyPI&label=Version&style=flat-square)](https://pypi.python.org/pypi/Dex-Starr/)
[![PyPI - License](https://img.shields.io/pypi/l/Dex-Starr.svg?logo=PyPI&label=License&style=flat-square)](https://opensource.org/licenses/GPL-3.0)

[![Black](https://img.shields.io/badge/Black-Enabled-000000?style=flat-square)](https://github.com/psf/black)
[![Flake8](https://img.shields.io/badge/Flake8-Enabled-informational?style=flat-square)](https://github.com/PyCQA/flake8)
[![Pre-Commit](https://img.shields.io/badge/Pre--Commit-Enabled-informational?logo=pre-commit&style=flat-square)](https://github.com/pre-commit/pre-commit)

[![Github - Contributors](https://img.shields.io/github/contributors/Buried-In-Code/Dex-Starr.svg?logo=Github&label=Contributors&style=flat-square)](https://github.com/Buried-In-Code/Dex-Starr/graphs/contributors)

[![Github Action - Code Analysis](https://img.shields.io/github/workflow/status/Buried-In-Code/Dex-Starr/Code%20Analysis?logo=Github-Actions&label=Code-Analysis&style=flat-square)](https://github.com/Buried-In-Code/Dex-Starr/actions/workflows/code-analysis.yaml)
[![Github Action - Testing](https://img.shields.io/github/workflow/status/Buried-In-Code/Dex-Starr/Testing?logo=Github-Actions&label=Tests&style=flat-square)](https://github.com/Buried-In-Code/Dex-Starr/actions/workflows/testing.yaml)

Dex-Starr helps sort and organize your comic collection by using the information stored in ComicInfo files.\
It also formats all your digital comics into a single format (CBZ) and transforms the `ComicInfo.xml` inside most digital comic files into either Json or Yaml.\
Dex-Starr can also pull information from a list of sources to populate missing fields.

## Supported File Formats:

- .cbz
- .cbr
- .cbt
- .cb7
- .cba

## Settings

All settings can be found in `~/.config/Dex-Starr/settings.yaml`\
*Requires restart for changes to take effect*

| Setting                           | Type        | Default               | Notes                                                                                               |
| --------------------------------- | ----------- | --------------------- | --------------------------------------------------------------------------------------------------- |
| `Output Format`                   | str         | Json                  | Sets the output format of the ComicInfo file in the Bundled Comic                                   |
| `Delete Extras`                   | bool        | False                 | Delete the old ComicInfo files, unless its the same as the output format, where it'll be overridden |
| `Resolution Order`                | list\[str\] | \[\]                  | Order of services to try and resolve when conflicting pulled data that will be used in ComicInfo    |
| `Import Folder`                   | str         | `~/Comics/Import`     | Folder to put in new Comics to be parsed by Dex-Starr                                               |
| `Processing Folder`               | str         | `~/Comics/Processing` | Folder where files go when the Comic is extracted                                                   |
| `Collection Folder`               | str         | `~/Comics/Collection` | Folder where all the comics are sorted and stored after Processing                                  |
| `Comicvine API Key`               | str         |                       | API Key used to authorize pulling information from [Comicvine](https://comicvine.gamespot.com/api/) |
| `League of Comic Geeks API Key`   | str         |                       |                                                                                                     |
| `League of Comic Geeks Client ID` | str         |                       |                                                                                                     |
| `Metron Username`                 | str         |                       | Username used to authorize pulling information from [Metron](https://metron.cloud/)                 |
| `Metron Password`                 | str         |                       | Password used to authorize pulling information fron [Metron](https://metron.cloud/)                 |

## Execution

### Arguments

| Argument                   | Type | Required | Default | Options         | Notes                                                                                |
| -------------------------- | ---- | -------- | ------- | --------------- | ------------------------------------------------------------------------------------ |
| `-o` `--set-output-format` | str  | False    |         | Json, Xml, Yaml | Changes the **output format** in settings                                            |
| `-d` `--set-delete-extras` | str  | False    |         | True, False     | Override the **keep extras** setting only for this run                               |
| `--manual-edit`            | bool | False    | False   |                 | Pause the Script before bundling up the files to allow manual removal of Ads, etc... |
| `--resolve-manually`       | bool | False    | False   |                 | Override the settings and manually choose which piece of data to use in ComicInfo    |
| `--debug`                  | bool | False    | False   |                 |                                                                                      |

### From Source

1. Make sure you have [Poetry](https://python-poetry.org) installed
2. Clone the repo: `git clone https://github.com/Buried-In-Code/Dex-Starr`
3. Navigate to the folder: `cd Dex-Starr/`
4. Run: `poetry install`
5. Run: `poetry run Dex-Starr`

### From PyPI

1. Run: `pip install Dex-Starr`
2. Run: `Dex-Starr`

## File Renaming

### Series Naming

Series with volume greater than 1 will display its volume in the title.

### Comic Naming

The files are named based on the format of Comic:

- Comic *(default)*: `{Series Title}-#{Issue Number}.cbz`
- Annual: `{Series Title}-Annual-#{Issue Number}.cbz`
- Digital Chapter: `{Series Title}-Chapter-#{Issue Number}.cbz`
- Hardcover *(If it is a numbered issue e.g. [](<>)*: `{Series Title}-#{Issue Number}-HC.cbz`
- Hardcover *(If it is not a numbered issue e.g. [](<>)*: `{Series Title}-{Issue Title}-HC.cbz`
- Trade Paperback *(If it is a numbered issue e.g. [The Flash v5 #3 TP](https://leagueofcomicgeeks.com/comic/6522430/the-flash-vol-3-rogues-reloaded-tp))*: `{Series Title}-#{Issue Number}-TP.cbz`
- Trade Paperback *(If it is not a numbered issue e.g. [The Amazing Spider-Man v2: One Moment in Time TP](https://leagueofcomicgeeks.com/comic/3063015/amazing-spider-man-one-moment-in-time-tp))*: `{Series Title}-{Issue Title}-TP.cbz`

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
|  |  |  +-- Series-#001.cbz
|  |  |  +-- Series-Annual-#01.cbz
|  |  |  +-- Series-Chapter-#01.cbz
|  |  |  +-- Series-#01-HC.cbz
|  |  |  +-- Series-Title-HC.cbz
|  |  |  +-- Series-#01-TP.cbz
|  |  |  +-- Series-Title-TP.cbz
|  |  +-- Series-v2
|  |  |  +-- Series-v2-#001.cbz
|  |  |  +-- Series-v2-Annual-#01.cbz
|  |  |  +-- Series-v2-Chapter-#01.cbz
|  |  |  +-- Series-v2-#01-HC.cbz
|  |  |  +-- Series-v2-Title-HC.cbz
|  |  |  +-- Series-v2-#01-TP.cbz
|  |  |  +-- Series-v2-Title-TP.cbz
```

## Socials

[![Social - Discord](https://img.shields.io/badge/Discord-The--DEV--Environment-7289DA?logo=Discord&style=flat-square)](https://discord.gg/nqGMeGg)
