from datetime import date


# Daily transfer limit per customer 
DAILY_TRANSFER_LIMIT = 5000

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
    today = date.today().isoformat()

    # Calculate how much the sender has already transferred today
    cursor.execute(
        """SELECT COALESCE(SUM(amount), 0)
           FROM transfer_transactions
           WHERE sender_pin = ? AND transaction_date = ?""",
        (account_id, today)
    )
    transferred_today = cursor.fetchone()[0]
    remaining_limit = DAILY_TRANSFER_LIMIT - transferred_today

    # Display account information
    print("\n===== TRANSFER FUNDS =====")
    print(f"Available balance: ${balance:,.2f}")
    print(f"Daily transfer limit: ${DAILY_TRANSFER_LIMIT:,.2f}")
    print(f"Transferred today: ${transferred_today:,.2f}")
    print(f"Remaining daily limit: ${max(remaining_limit, 0):,.2f}")

    # Check if the daily transfer limit has been reached
    if remaining_limit <= 0:
        print("You have reached your daily transfer limit.")
        return

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
    if amount > remaining_limit:
        print(f"Amount exceeds your remaining daily transfer limit of ${remaining_limit:,.2f}.")
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
        (account_id, receiver[0], amount, today)
    )

    print(f"Transfer successful! Your new balance is: ${balance - amount:,.2f}")
