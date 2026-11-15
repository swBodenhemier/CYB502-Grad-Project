import hashlib
import json

from cyb502_grad_project.transaction import Transaction


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class MerkleTree:
    @staticmethod
    def transaction_bytes(transaction: Transaction) -> bytes:
        data = transaction.model_dump(mode="json")
        return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")

    @classmethod
    def leaf_hash(cls, transaction: Transaction) -> str:
        return sha256_hex(cls.transaction_bytes(transaction))

    @classmethod
    def root(cls, transactions: list[Transaction]) -> str:
        if not transactions:
            return sha256_hex(b"")

        level = [cls.leaf_hash(transaction) for transaction in transactions]

        while len(level) > 1:
            if len(level) % 2 == 1:
                level.append(level[-1])

            level = [
                sha256_hex(bytes.fromhex(level[i]) + bytes.fromhex(level[i + 1]))
                for i in range(0, len(level), 2)
            ]

        return level[0]

    @classmethod
    def proof(
        cls, transactions: list[Transaction], transaction_index: int
    ) -> list[dict[str, str]]:
        # Return the sibling hashes needed to prove a transaction's inclusion
        if not 0 <= transaction_index < len(transactions):
            raise IndexError("Transaction index is out of range")

        level = [cls.leaf_hash(transaction) for transaction in transactions]
        index = transaction_index
        proof = []

        while len(level) > 1:
            if len(level) % 2 == 1:
                level.append(level[-1])

            sibling_index = index - 1 if index % 2 else index + 1
            proof.append(
                {
                    "hash": level[sibling_index],
                    "side": "left" if index % 2 else "right",
                }
            )

            level = [
                sha256_hex(bytes.fromhex(level[i]) + bytes.fromhex(level[i + 1]))
                for i in range(0, len(level), 2)
            ]
            index //= 2

        return proof

    @classmethod
    def verify_proof(
        cls,
        transaction: Transaction,
        proof: list[dict[str, str]],
        expected_root: str,
    ) -> bool:
        current_hash = cls.leaf_hash(transaction)

        try:
            for step in proof:
                sibling_hash = step["hash"]
                side = step["side"]

                if side == "left":
                    combined = bytes.fromhex(sibling_hash) + bytes.fromhex(current_hash)
                elif side == "right":
                    combined = bytes.fromhex(current_hash) + bytes.fromhex(sibling_hash)
                else:
                    return False

                current_hash = sha256_hex(combined)
        except:
            return False

        return current_hash == expected_root
