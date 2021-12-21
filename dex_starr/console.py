import logging
from datetime import date, datetime
from typing import Any, List, Optional

from rich import inspect
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.theme import Theme


class ConsoleLog:
    def __init__(self, name: str):
        self.console = Console(
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
        self.logger = logging.getLogger(name)

    def panel(self, title: str, style: Optional[str] = None, expand: bool = True):
        self.console.print(Panel(title, expand=expand), style=style, justify="center")
        self.logger.info(title)

    def rule(self, title: str, text_style: str = "rule.line", line_style: str = "rule.line"):
        self.console.rule(title=f"[{text_style}]{title}[/]", style=line_style)
        self.logger.info(title)

    def prompt(
        self,
        prompt: str,
        password: bool = False,
        choices: Optional[List[str]] = None,
        default: Optional[str] = None,
        require_response: bool = True,
    ) -> Optional[str]:
        prompt_str = prompt
        if choices:
            prompt_str += f" [prompt.choices][{', '.join(choices)}][/]"
        if default:
            prompt_str += f" [prompt.default]({default})[/]"
        response = self.console.input(prompt=f"[prompt]{prompt_str} >> [/]", password=password).strip()
        if response:
            if not choices:
                return response
            elif response in choices:
                return response
        if default:
            return default
        if require_response:
            return self.prompt(prompt=prompt, password=password, choices=choices, default=default)
        return None

    def prompt_int(
        self,
        prompt: str,
        choices: Optional[List[int]] = None,
        default: Optional[int] = None,
        require_response: bool = True,
    ) -> Optional[int]:
        try:
            return int(self.prompt(prompt=prompt, choices=choices, default=default))
        except ValueError:
            return (
                default
                if default
                else self.prompt_int(prompt=prompt, choices=choices, default=default)
                if require_response
                else None
            )

    def prompt_float(
        self,
        prompt: str,
        choices: Optional[List[float]] = None,
        default: Optional[float] = None,
        require_response: bool = True,
    ) -> Optional[float]:
        try:
            return float(self.prompt(prompt=prompt, choices=choices, default=default))
        except ValueError:
            return (
                default
                if default
                else self.prompt_float(prompt=prompt, choices=choices, default=default)
                if require_response
                else None
            )

    def prompt_bool(self, prompt: str) -> bool:
        return self.prompt(prompt=prompt, choices=["Y", "N"], require_response=True) == "Y"

    def prompt_date(
        self,
        prompt: str,
        choices: Optional[List[date]] = None,
        default: Optional[date] = None,
        require_response: bool = True,
    ) -> Optional[date]:
        prompt += " {YYYY-MM-DD}"
        try:
            date.fromisoformat(
                self.prompt(prompt, choices=[x.isoformat() for x in choices] if choices else None, default=default)
            )
        except ValueError:
            return (
                default
                if default
                else self.prompt_date(prompt=prompt, choices=choices, default=default)
                if require_response
                else None
            )

    def prompt_datetime(
        self,
        prompt: str,
        choices: Optional[List[datetime]] = None,
        default: Optional[datetime] = None,
        require_response: bool = True,
    ) -> Optional[datetime]:
        prompt += " {YYYY-MM-DDTHH:MM:SS}"
        try:
            datetime.fromisoformat(
                self.prompt(prompt, choices=[x.isoformat() for x in choices] if choices else None, default=default)
            )
        except ValueError:
            return (
                default
                if default
                else self.prompt_datetime(prompt=prompt, choices=choices, default=default)
                if require_response
                else None
            )

    def menu(self, options: List[str], prompt: Optional[str] = None, none_option: bool = True) -> Optional[int]:
        if len(options) == 0:
            return 0
        for index, item in enumerate(options):
            self.print_item_value(item=str(index + 1), value=item)
        if none_option:
            self.print_item_value(item="0", value="None of the Above")
        return self.prompt_int(prompt, default=0 if none_option else None, require_response=True)

    def print_dict(self, data: Any, title: Optional[str] = None, subtitle: Optional[str] = None):
        json_data = JSON.from_data(
            data,
            indent=2,
            highlight=True,
            skip_keys=False,
            ensure_ascii=True,
            check_circular=True,
            allow_nan=True,
            default=None,
            sort_keys=False,
        )
        self.console.print(Panel(json_data, title=title, subtitle=subtitle), style="logging.level.error")

    def print_item_value(self, item: str, value: str):
        self.console.print(f"[magenta]{item}:[/] {value}")

    def print(self, text: str):
        self.console.print(text)

    def debug(self, text: Optional[str] = None, object_: Any = None):
        if object_:
            inspect(object_, title=text, methods=True)
        else:
            self.console.print(f"[logging.level.debug]{text}[/]")
        self.logger.debug(text)

    def info(self, text: Optional[str] = None, object_: Any = None):
        if object_:
            inspect(object_, title=text)
        else:
            self.console.print(f"[logging.level.info]{text}[/]")
        self.logger.info(text)

    def warning(self, text: Optional[str] = None, object_: Any = None):
        if object_:
            inspect(object_, title=text)
        else:
            self.console.print(f"[logging.level.warning]{text}[/]")
        self.logger.warning(text)

    def error(self, text: Optional[str] = None, object_: Any = None):
        if object_:
            inspect(object_, title=text)
        else:
            self.console.print(f"[logging.level.error]{text}[/]")
        self.logger.error(text)

    def critical(self, text: Optional[str] = None, object_: Any = None):
        if object_:
            inspect(object_, title=text)
        else:
            self.console.print(f"[logging.level.critical]{text}[/]")
        self.logger.critical(text)
