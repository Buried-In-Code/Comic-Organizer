import logging
from enum import Enum, unique
from typing import List, Optional

from colorama import Fore, Style, init

LOGGER = logging.getLogger(__name__)

init(autoreset=True, strip=False)


@unique
class Colour(Enum):
    BLACK = (Style.NORMAL, Fore.BLACK)
    RED = (Style.NORMAL, Fore.RED)
    GREEN = (Style.NORMAL, Fore.GREEN)
    YELLOW = (Style.NORMAL, Fore.YELLOW)
    BLUE = (Style.NORMAL, Fore.BLUE)
    MAGENTA = (Style.NORMAL, Fore.MAGENTA)
    CYAN = (Style.NORMAL, Fore.CYAN)
    WHITE = (Style.NORMAL, Fore.WHITE)

    def __init__(self, style: Style, fore: Fore):
        self.__style = style
        self.__fore = fore

        self.style = style + fore

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"{type(self).__name__}({self.name})"


class Console:
    @classmethod
    def display_heading(cls, text: str):
        cls.__colour_console(text="=" * (len(text) + 4), colour=Colour.BLUE)
        cls.display_sub_heading(text=text)
        cls.__colour_console(text="=" * (len(text) + 4), colour=Colour.BLUE)

    @classmethod
    def display_sub_heading(cls, text: str):
        cls.__colour_console(text=f"  {text}  ", colour=Colour.BLUE)

    @classmethod
    def request_str(cls, prompt: Optional[str] = None) -> str:
        prompt = f"{prompt} >> " if prompt else ">> "
        cls.__colour_console(text=prompt, colour=Colour.GREEN, end="")
        return input()

    @classmethod
    def request_int(cls, prompt: Optional[str] = None) -> Optional[int]:
        try:
            return int(cls.request_str(prompt))
        except ValueError:
            LOGGER.error("Invalid Integer")
            return None

    @classmethod
    def request_float(cls, prompt: Optional[str] = None) -> Optional[float]:
        try:
            return float(cls.request_str(prompt))
        except ValueError:
            LOGGER.error("Invalid Float")
            return None

    @classmethod
    def request_bool(cls, prompt: Optional[str] = None) -> bool:
        prompt = f"{prompt} [Y/N]" if prompt else "[Y/N]"
        return cls.request_str(prompt=prompt).lower() == "y"

    @classmethod
    def display_text(cls, text: str):
        cls.__colour_console(text=text)

    @classmethod
    def display_item_value(cls, item: str, value: str):
        cls.__colour_console(text=f"{item}: ", colour=Colour.MAGENTA, end="")
        cls.__colour_console(text=value)

    @classmethod
    def display_menu(cls, items: List[str], prompt: Optional[str] = None, exit_text: Optional[str] = None) -> int:
        if len(items) == 0:
            return 0
        for index, item in enumerate(items):
            cls.display_item_value(item=str(index + 1), value=item)
        if exit_text:
            cls.display_item_value(item="0", value=exit_text)
        return cls.request_int(prompt) or 0

    @classmethod
    def __colour_console(cls, text: str, colour: Colour = Colour.WHITE, end: Optional[str] = None):
        print(f"{colour.style}{text}{Style.RESET_ALL}", end=end)
