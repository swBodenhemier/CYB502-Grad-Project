import json
from datetime import UTC, datetime
from time import time
from typing import Self

from pydantic import BaseModel

from cyb502_grad_project.merkle_tree import MerkleTree, sha256_hex
from cyb502_grad_project.transaction import Transaction


class Block(BaseModel):
    index: int
    timestamp: datetime
    transactions: list[Transaction]
    merkle_root: str
    hash: str
    prev_hash: str | None = None
    nonce: int = 0

    @classmethod
    def create(
        cls,
        prev: Self | None = None,
        transactions: list[Transaction] | None = None,
    ) -> Self:
        index = 0 if prev is None else prev.index + 1
        prev_hash = None if prev is None else prev.hash
        timestamp = datetime.now(UTC)
        nonce = 0

        merkle_root = MerkleTree.root(transactions)
        block_hash = cls.make_hash(index, timestamp, merkle_root, prev_hash, nonce)

        return cls(
            index=index,
            timestamp=timestamp,
            transactions=[] if transactions is None else transactions,
            merkle_root=merkle_root,
            hash=block_hash,
            prev_hash=prev_hash,
            nonce=nonce,
        )

    @staticmethod
    def make_hash(
        index: int,
        timestamp: datetime,
        merkle_root: str,
        prev_hash: str | None,
        nonce: int,
    ) -> str:
        block_data = {
            "index": index,
            "timestamp": timestamp.isoformat(),
            "merkle_root": merkle_root,
            "prev_hash": prev_hash,
            "nonce": nonce,
        }
        encoded = json.dumps(block_data, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
        return sha256_hex(encoded)

    def print_block(self) -> None:
        transaction_str = ",".join(
            f"""
            (
                Sender: {transaction.sender}
                Recipient: {transaction.recipient}
                Amount: {transaction.amount}
            )"""
            for transaction in self.transactions
        )

        print(f"""
-------------------------------------
    Index: {self.index}
    Timestamp: {self.timestamp}
    Transactions: [{transaction_str}]
    Merkle Tree Root: {self.merkle_root}
    Nonce: {self.nonce}
    Previous Hash: {self.prev_hash}
    Hash: {self.hash}
-------------------------------------
        """)

    def validate_block(self, chain: list[Self]) -> tuple[bool, str]:
        # recompute the hash to check for modifications in the block
        hash_check = self.make_hash(
            self.index, self.timestamp, self.merkle_root, self.prev_hash, self.nonce
        )
        if hash_check != self.hash:
            return (
                False,
                f"Block hash does not match calculated hash, block with index {self.index} has been modified.",
            )

        # validate every transaction in the block
        for index, _ in enumerate(self.transactions):
            proof = MerkleTree.proof(self.transactions, index)
            if not self.validate_transaction(index, proof):
                return (False, f"Transaction at index {index} has been modified.")

        # validate the previous block if it exists
        if self.index == 0:
            return (True, "")
        else:
            return chain[self.index - 1].validate_block(chain)

    def validate_transaction(
        self,
        transaction_index: int,
        proof: list[dict[str, str]],
    ) -> bool:
        # Check that the indexed transaction in the block matches its Merkle proof
        if not 0 <= transaction_index < len(self.transactions):
            return False

        transaction = self.transactions[transaction_index]

        # Recompute the root from all transactions to detect modifications
        if MerkleTree.root(self.transactions) != self.merkle_root:
            return False

        return MerkleTree.verify_proof(transaction, proof, self.merkle_root)

    def mine_block(self, difficulty: int = 4) -> Self:
        target_prefix = "0" * difficulty
        self.nonce = 0
        last_check = time()

        while True:
            # check in every 5 seconds so the user know's work is happening
            now = time()
            if now - last_check >= 5:
                print(f"    Working... (nonce: {self.nonce})")
                last_check = now

            # make a new hash with the updated nonce
            self.hash = self.make_hash(
                self.index,
                self.timestamp,
                self.merkle_root,
                self.prev_hash,
                self.nonce,
            )

            # check whether the computed hash is valid
            if self.hash.startswith(target_prefix):
                return self

            self.nonce += 1


def mine_chain(chain: list[Block], difficulty: int = 4) -> Block:
    block = chain[-1]

    # Keep the block linked to the preceding block before mining it.
    if len(chain) > 1:
        block.prev_hash = chain[-2].hash

    return block.mine_block(difficulty)
