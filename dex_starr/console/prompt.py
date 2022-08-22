from __future__ import annotations

from datetime import date, datetime

from rich.prompt import DefaultType, InvalidResponse, PromptBase, Text


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
