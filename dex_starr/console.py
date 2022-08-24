__all__ = [
    "CONSOLE",
    "DatePrompt",
    "DatetimePrompt",
    "create_menu",
]

from datetime import date, datetime
from typing import List, Optional

from rich.console import Console
from rich.prompt import DefaultType, IntPrompt, InvalidResponse, PromptBase, Text
from rich.theme import Theme

CONSOLE = Console(
    theme=Theme(
        {
            "prompt": "green",
            "prompt.choices": "white",
            "prompt.default": "dim italic white",
            "logging.level.debug": "dim italic white",
            "logging.level.info": "white",
            "logging.level.warning": "red",
            "logging.level.error": "bold red",
            "logging.level.critical": "magenta",
        }
    )
)


class DatePrompt(PromptBase[date]):
    response_type = date
    validate_error_message = "[prompt.invalid]Please enter a valid ISO-8601 date"

    def render_default(self, default: DefaultType) -> Text:
        return Text(default.isoformat() if default else "", style="prompt.default")

    def check_choice(self, value: str) -> bool:
        assert self.choices is not None
        try:
            return date.fromisoformat(value.strip()) in self.choices
        except ValueError:
            return False

    def process_response(self, value: str) -> date:
        try:
            mapped_value = date.fromisoformat(value.strip())
        except ValueError:
            raise InvalidResponse(self.validate_error_message)

        if self.choices is not None and not self.check_choice(value):
            raise InvalidResponse(self.illegal_choice_message)

        return mapped_value


class DatetimePrompt(PromptBase[datetime]):
    response_type = datetime
    validate_error_message = "[prompt.invalid]Please enter a valid ISO-8601 datetime"

    def render_default(self, default: DefaultType) -> Text:
        return Text(default.isoformat() if default else "", style="prompt.default")

    def check_choice(self, value: str) -> bool:
        assert self.choices is not None
        try:
            return datetime.fromisoformat(value.strip()) in self.choices
        except ValueError:
            return False

    def process_response(self, value: str) -> datetime:
        try:
            mapped_value = datetime.fromisoformat(value.strip())
        except ValueError:
            raise InvalidResponse(self.validate_error_message)

        if self.choices is not None and not self.check_choice(value):
            raise InvalidResponse(self.illegal_choice_message)

        return mapped_value


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
