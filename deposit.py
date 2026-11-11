from datetime import date

def deposit_money(cursor, account_id):

    # Create a table to store deposit transactions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deposit_transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pin_number TEXT NOT NULL,
            amount INTEGER NOT NULL,
            transaction_date TEXT NOT NULL
        )
    """)

    # Get the customer's balance and daily deposit limit
    cursor.execute(
        "SELECT balance, deposit_limit FROM atm WHERE pin_number = ?",
        (account_id,)
    )
    account = cursor.fetchone()

    # Check if the account exists
    if account is None:
        print("Account not found. Deposit cancelled.")
        return

    balance, daily_limit = account
    today = date.today().isoformat()

    # Calculate the total amount deposited today
    cursor.execute(
        """SELECT COALESCE(SUM(amount), 0)
           FROM deposit_transactions
           WHERE pin_number = ? AND transaction_date = ?""",
        (account_id, today)
    )
    deposited_today = cursor.fetchone()[0]

    # Calculate the remaining daily deposit limit
    remaining_limit = daily_limit - deposited_today

    # Display account information
    print("\n===== DEPOSIT FUNDS =====")
    print(f"Current balance: ${balance:,.2f}")
    print(f"Daily deposit limit: ${daily_limit:,.2f}")
    print(f"Deposited today: ${deposited_today:,.2f}")
    print(f"Remaining daily limit: ${max(remaining_limit, 0):,.2f}")

    # Check if the daily deposit limit has been reached
    if remaining_limit <= 0:
        print("You have reached your daily deposit limit.")
        return

    # Ask the customer to enter the deposit amount
    try:
        amount_input = input("\nEnter deposit amount: $")
        amount = float(amount_input.replace(",", "").replace("$", ""))

        if not amount.is_integer():
            print("Please enter a whole dollar amount.")
            return

        amount = int(amount)

    except ValueError:
        print("Invalid amount. Please enter a whole number.")
        return

    # Validate the deposit amount
    if amount <= 0:
        print("Deposit amount must be greater than zero.")
        return

    # Check if the amount exceeds the remaining daily limit
    if amount > remaining_limit:
        print(
            f"Amount exceeds your remaining daily deposit limit "
            f"of ${remaining_limit:,.2f}."
        )
        return

    # Display the deposit summary
    print("\n===== DEPOSIT SUMMARY =====")
    print(f"Deposit amount: ${amount:,.2f}")
    print(f"Current balance: ${balance:,.2f}")
    print(f"New balance: ${balance + amount:,.2f}")

    # Ask the customer to confirm the deposit
    confirm = input("\nConfirm deposit? (Y/N): ").strip().upper()

    # Cancel the transaction if the customer does not confirm
    if confirm != "Y":
        print("Deposit cancelled. Your balance has not changed.")
        return

    # Recheck the balance and daily deposit limit before processing
    cursor.execute(
        "SELECT balance, deposit_limit FROM atm WHERE pin_number = ?",
        (account_id,)
    )
    current_account = cursor.fetchone()

    if current_account is None:
        print("Account not found. Deposit cancelled.")
        return

    current_balance, current_daily_limit = current_account

    # Get the latest total deposits for today
    cursor.execute(
        """SELECT COALESCE(SUM(amount), 0)
           FROM deposit_transactions
           WHERE pin_number = ? AND transaction_date = ?""",
        (account_id, today)
    )
    current_deposited_today = cursor.fetchone()[0]

    # Make sure the transaction is still within the daily limit
    if current_deposited_today + amount > current_daily_limit:
        print("The daily deposit limit has changed. Please try again.")
        return

    # Add the deposit amount to the account balance
    cursor.execute(
        "UPDATE atm SET balance = balance + ? WHERE pin_number = ?",
        (amount, account_id)
    )

    # Save the deposit details in the transaction history
    cursor.execute(
        """INSERT INTO deposit_transactions
           (pin_number, amount, transaction_date)
           VALUES (?, ?, ?)""",
        (account_id, amount, today)
    )

    # Display the successful transaction message
    print("\nDeposit successful!")
    print(f"Your new balance is: ${current_balance + amount:,.2f}")