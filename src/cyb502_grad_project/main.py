import sys
from datetime import datetime

from pydantic import TypeAdapter

from cyb502_grad_project.block import Block, mine_chain
from cyb502_grad_project.transaction import generate_transactions

json_adaptor = TypeAdapter(list[Block])


def main():
    chain: list[Block] = []

    usage = """Usage:
    (1): Create a new block
    (2): Print a block
    (3): Print the whole chain
    (4): Validate the chain
    (5): Mine the chain

    (s): Save chain to json file
    (l): Load chain from json file (replace current chain)

    (m): Modify the chain (to test validation)

    (h): Print usage
    (q): Quit
    """
    invalid_count = 0
    print("Welcome to our blockchain implementation.")
    print(usage)

    while True:
        action = input("\nInput your action: ")

        if action == "1":
            print("    Creating a new block")
            num_transactions = int(input("    Number of transactions to generate: "))
            transactions = generate_transactions(max(num_transactions, 0))
            block = Block.create(
                prev=None if len(chain) == 0 else chain[len(chain) - 1],
                transactions=transactions,
            )
            chain.append(block)
            print(f"    Block successfully created with index: {block.index}")

        elif action == "2":
            if len(chain) == 0:
                print("    Chain is empty")
                continue
            print(f"    Chain length: {len(chain)}")
            index = int(input("    Block Index to print: "))
            if index < len(chain) and index >= 0:
                chain[index].print_block()
            else:
                print("    Index out of range.")

        elif action == "3":
            if len(chain) == 0:
                print("    Chain is empty")
                continue
            for block in chain:
                block.print_block()

        elif action == "4":
            print("    Validating chain...")
            valid = chain[len(chain) - 1].validate_block(chain)
            if valid[0]:
                print("    Chain is valid")
            else:
                print(f"    ! Chain is Invalid: \n        {valid[1]}")

        elif action == "5":
            if len(chain) == 0:
                print("    Chain is empty")
                continue

            difficulty = 0
            try:
                difficulty = int(input("    Mine with difficulty: "))
            except:
                print("    Difficulty must be an integer")
                continue
            print("    Mining chain...")
            mine_chain(chain, max(difficulty, 0))
            print(f"\n    Mining Complete with nonce: {chain[len(chain) - 1].nonce}")

        elif action == "s":
            if len(chain) == 0:
                print("    Chain is empty")
                continue

            print("    Saving chain to json file")
            file_name = input("    Enter file name: ")
            file_name = (
                file_name if file_name.endswith(".json") else f"{file_name}.json"
            )

            try:
                with open(file_name, "wb") as file:
                    file.write(json_adaptor.dump_json(chain, indent=4))
                print(f"    Successfully wrote chain to {file_name}")
            except:
                print("    Failed to save chain to disk")

        elif action == "l":
            print(
                "    Loading chain from json file\n"
                '      NOTE: this will replace the current chain, enter "q" to go back\n'
            )
            file_name = input("    Enter file name: ")
            if file_name == "q":
                continue

            file_name = (
                file_name if file_name.endswith(".json") else f"{file_name}.json"
            )
            prev_chain = chain

            try:
                with open(file_name, "r") as file:
                    chain = json_adaptor.validate_json(file.read())
            except:
                print("    Failed to load chain from disk")
                chain = prev_chain

        elif action == "m":
            if len(chain) == 0:
                print("    Chain is empty")
                continue

            print(
                f"    Modifying the chain (length: {len(chain)})\n"
                '      NOTE: this will make the chain invalid, enter "q" to go back\n'
            )

            block_index = 0
            try:
                block_index = int(input("    Enter the block index to modify: "))
            except:
                print("    Block index must be an integer")
                continue
            if block_index == "":
                continue
            elif block_index >= len(chain) or block_index < 0:
                print("    Index out of range.")
                continue

            block = chain[block_index]
            print("""
    Choose what to modify
        (h): hash
        (ph): prev_hash
        (tm): timestamp
        (tx): transactions""")
            modifying = input("    ")

            if modifying == "h":
                new_val = input("        Enter new hash value: ")
                block.hash = new_val

            elif modifying == "ph":
                new_val = input("        Enter new prev_hash value: ")
                block.prev_hash = new_val

            elif modifying == "tm":
                new_val = input("        Enter new timestamp value in ISO format: ")
                block.timestamp = datetime.fromisoformat(new_val)

            elif modifying == "tx":
                if len(block.transactions) == 0:
                    print("        Block has no transactions.")
                    continue
                print(f"""
        Choose how to modify transactions
            (n): create a new transaction
            (d): delete a transaction
            (0{f"-{len(block.transactions) - 1}" if len(block.transactions) > 0 else ""}): Edit transactions at index""")
                choice = input("        ")

                if choice == "n":
                    block.transactions.append(generate_transactions(1)[0])

                elif choice == "d":
                    block.transactions.pop()

                else:
                    tx_index = int(choice)
                    if (
                        tx_index
                        and tx_index >= 0
                        and tx_index < len(block.transactions)
                    ):
                        block.transactions[tx_index] = generate_transactions(1)[0]
                    else:
                        continue
            else:
                continue
            print("    Block modified")

        elif action == "h":
            print(usage)

        elif action == "q":
            print("    Exiting")
            sys.exit(0)

        else:
            invalid_count += 1
            print("    Invalid action")
            if invalid_count >= 3:
                print(usage)
                invalid_count = 0


if __name__ == "__main__":
    main()
