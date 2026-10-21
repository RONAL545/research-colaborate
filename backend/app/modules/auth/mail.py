from dataclasses import dataclass, field
from typing import Protocol


class Mailer(Protocol):
    def send_verification(self, email: str, token: str) -> None: ...


class UnconfiguredMailer:
    def send_verification(self, email: str, token: str) -> None:
        # No delivery and no logging of credentials without a configured provider.
        pass


@dataclass
class TestMailbox:
    __test__ = False
    messages: list[tuple[str, str]] = field(default_factory=list)

    def send_verification(self, email: str, token: str) -> None:
        self.messages.append((email, token))


def get_mailer() -> Mailer:
    return UnconfiguredMailer()
