from datetime import date

def transfer_funds(cursor, account_id):

    # Table for the transfer history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transfer_transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_pin TEXT NOT NULL,
            receiver_pin TEXT NOT NULL,
            amount INTEGER NOT NULL,
            transaction_date TEXT NOT NULL
        )
    """)

    # Get the sender's balance
    cursor.execute("SELECT balance FROM atm WHERE pin_number = ?", (account_id,))
    balance = cursor.fetchone()[0]
    print(f"\nAvailable balance: ${balance:,.2f}")

    # Find the receiver by username
    receiver_name = input("Enter the receiver's username: ").strip()
    cursor.execute("SELECT pin_number FROM atm WHERE username = ?", (receiver_name,))
    receiver = cursor.fetchone()

    if receiver is None:
        print("Receiver not found. Transfer cancelled.")
        return
    if receiver[0] == account_id:
        print("You cannot transfer to your own account.")
        return

    # Read and validate the amount
    try:
        amount = int(input("Enter transfer amount (whole dollars): $"))
    except ValueError:
        print("Invalid amount. Please enter a whole number.")
        return
    if amount <= 0:
        print("Transfer amount must be greater than zero.")
        return
    if amount > balance:
        print("Insufficient funds.")
        return

    # Confirm
    if input(f"Send ${amount:,.2f} to {receiver_name}? (Y/N): ").strip().upper() != "Y":
        print("Transfer cancelled.")
        return

    # Update both accounts (runner.py commits)
    cursor.execute("UPDATE atm SET balance = balance - ? WHERE pin_number = ?", (amount, account_id))
    cursor.execute("UPDATE atm SET balance = balance + ? WHERE pin_number = ?", (amount, receiver[0]))

    # Save the transfer in the history
    cursor.execute(
        "INSERT INTO transfer_transactions (sender_pin, receiver_pin, amount, transaction_date) VALUES (?, ?, ?, ?)",
        (account_id, receiver[0], amount, date.today().isoformat())
    )

    print(f"Transfer successful! Your new balance is: ${balance - amount:,.2f}")
