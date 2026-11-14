import random
import secrets

from pydantic import BaseModel


class Transaction(BaseModel):
    sender: str
    recipient: str
    amount: float


def generate_transactions(num: int) -> list[Transaction]:
    transactions = []
    for _ in range(num):
        transactions.append(
            Transaction(
                sender=secrets.token_hex(16),
                recipient=secrets.token_hex(16),
                amount=round(random.random() * 200, 2),
            )
        )
    return transactions
