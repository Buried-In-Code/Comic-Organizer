from typing import List, Optional, Union

from rich import box
from rich.console import Console
from rich.progress import BarColumn, Column, Progress, TextColumn, TimeElapsedColumn
from rich.prompt import IntPrompt
from rich.table import Table
from rich.theme import Theme

CONSOLE = Console(
    theme=Theme(
        {
            "prompt": "green",
            "prompt.choices": "italic yellow",
            "prompt.default": "dim yellow",
            "logging.level.debug": "dim white",
            "logging.level.info": "white",
            "logging.level.warning": "yellow",
            "logging.level.error": "red",
            "logging.level.critical": "bold red",
            "bar.back": "dim bright_black",
            "bar.complete": "yellow",
            "bar.finished": "green",
        }
    )
)


def create_menu(
    options: List[str], prompt: Optional[str] = None, default: Optional[str] = None
) -> Optional[int]:
    if not options:
        return 0
    for index, item in enumerate(options):
        CONSOLE.print(f"[prompt]{index + 1}:[/] [prompt.choices]{item}[/]")
    if default:
        CONSOLE.print(f"[prompt]0:[/] [prompt.default]{default}[/]")
    selected = IntPrompt.ask(prompt=prompt, default=0 if default else None, console=CONSOLE)
    if selected < 0 or selected > len(options) or (selected == 0 and not default):
        CONSOLE.print(f"Invalid Option: `{selected}`", style="prompt.invalid")
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


def create_table(columns: List[Union[str, Column]], title: str = "", show_footer: bool = False):
    return Table(
        *columns,
        title=title,
        expand=True,
        box=box.SIMPLE,
        style="blue",
        title_style="bold magenta",
        header_style="bold blue",
        row_styles=["dim", ""],
        footer_style="blue",
        show_footer=show_footer,
    )
