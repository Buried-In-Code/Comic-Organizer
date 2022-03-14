from typing import Any, List, Optional, Tuple

from rich.console import Console
from rich.progress import BarColumn, Column, Progress, TextColumn, TimeElapsedColumn
from rich.prompt import IntPrompt
from rich.table import Table as RichTable
from rich.theme import Theme

CONSOLE = Console(
    theme=Theme(
        {
            "prompt": "green",
            "prompt.format": "dim italic green",
            "prompt.choices": "dim yellow",
            "prompt.default": "italic yellow",
            "logging.level.debug": "dim blue",
            "logging.level.info": "dim white",
            "logging.level.warning": "yellow",
            "logging.level.error": "red",
            "logging.level.critical": "magenta",
            "json.key": "bold green",
            "json.brace": "white",
            "json.str": "yellow",
            "json.number": "magenta",
            "json.null": "italic white",
        }
    )
)


class Table:
    def __init__(self, title: Optional[str] = None):
        self.title = title
        self.headers = []
        self.rows = []

    def add_columns(self, columns: List[Tuple[str, type]]):
        for title, type_ in columns:
            self.add_column(title=title, type_=type_)

    def add_column(self, title: str, type_: type):
        style = "json.number" if type_ in [int, float] else "json.str"
        justify = "right" if type_ in [int, float] else "left"
        self.headers.append((title, style, justify))

    def add_row(self, entries: List[Any]):
        self.rows.append([str(x) for x in entries])

    def display(self, console: Console = CONSOLE):
        table = RichTable(title=self.title)
        for title, style, justify in self.headers:
            table.add_column(title, style=style, justify=justify)
        for row in self.rows:
            table.add_row(*row)
        console.print(table)


def create_menu(
    options: List[str], prompt: Optional[str] = None, default: Optional[str] = None
) -> Optional[int]:
    if not options:
        return 0
    for index, item in enumerate(options):
        CONSOLE.print(f"[magenta]{index + 1}:[/] {item}")
    if default:
        CONSOLE.print(f"[magenta]0:[/] {default}")
    selected = IntPrompt.ask(prompt=prompt, default=0 if default else None, console=CONSOLE)
    if selected < 0 or selected > len(options) or (selected == 0 and not default):
        CONSOLE.print(f"Invalid Option: `{selected}`", style="logging.level.warning")
        return create_menu(options=options, prompt=prompt, default=default)
    return selected


def create_progress_bar() -> Progress:
    description_column = TextColumn("{task.description}", table_column=Column(ratio=2))
    progress_column = BarColumn(bar_width=None, table_column=Column(ratio=1))
    percentage_column = TextColumn(
        "[progress.percentage]{task.percentage:>3.0f}%", table_column=Column(ratio=1)
    )
    elapsed_column = TimeElapsedColumn(table_column=Column(ratio=1))
    return Progress(
        description_column,
        progress_column,
        percentage_column,
        elapsed_column,
        expand=True,
        console=CONSOLE,
    )
