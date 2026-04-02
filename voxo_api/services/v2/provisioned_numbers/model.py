from dataclasses import dataclass


@dataclass
class ProvisionedNumber:
    number: str


@dataclass
class ProvisionedNumbersResponse:
    provisionedNumbers: list
    total: int

    def __post_init__(self):
        self.provisionedNumbers = [
            ProvisionedNumber(**p) for p in self.provisionedNumbers
        ]
