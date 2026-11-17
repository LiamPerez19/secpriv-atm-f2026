from datetime import date
from time import time
import cash_handler

def withdraw_money(cursor, account_id):

    # Create a table to store withdrawal transactions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS withdrawal_transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pin_number TEXT NOT NULL,
            amount INTEGER NOT NULL,
            bills_20 INTEGER NOT NULL,
            bills_10 INTEGER NOT NULL,
            bills_5 INTEGER NOT NULL,
            transaction_date TEXT NOT NULL
        )
    """)

    # Get the customer's balance and daily withdrawal limit
    cursor.execute(
        "SELECT balance, withdraw_limit FROM atm WHERE pin_number = ?",
        (account_id,)
    )
    account = cursor.fetchone()

    # Check if the account exists
    if account is None:
        print("Account not found. Withdrawal cancelled.")
        return time()

    balance, daily_limit = account
    today = date.today().isoformat()

    # Calculate the total amount withdrawn today
    cursor.execute(
        """SELECT COALESCE(SUM(amount), 0)
           FROM withdrawal_transactions
           WHERE pin_number = ? AND transaction_date = ?""",
        (account_id, today)
    )
    withdrawn_today = cursor.fetchone()[0]

    # Grab how many bills are in the machine
    billcount = []
    for denom in [20,10,5]:
        cursor.execute(
            "SELECT quantity FROM atm_cash WHERE denomination = ?",
            (denom,)
        )
        billcount.append(cursor.fetchone())
    
    twenties = billcount[0][0]
    tens = billcount[1][0]
    fives = billcount[2][0]

    # Calculate the remaining daily withdrawal limit
    remaining_limit = daily_limit - withdrawn_today

    # Display account information
    print("\n===== WITHDRAW FUNDS =====")
    print(f"Available balance: ${balance:,.2f}")
    print(f"Daily withdrawal limit: ${daily_limit:,.2f}")
    print(f"Withdrawn today: ${withdrawn_today:,.2f}")
    print(f"Remaining daily limit: ${max(remaining_limit, 0):,.2f}")
    print(f"Bills in machine: $20 - {twenties}, $10 - {tens}, $5 - {fives}")

    # Check if the daily withdrawal limit has been reached
    if remaining_limit <= 0:
        print("You have reached your daily withdrawal limit.")
        return time()

    start_time = time() 

    # Ask the customer to enter the withdrawal amount
    try:
        amount = int(input("\nEnter withdrawal amount (whole dollars): $"))
    except ValueError:
        print("Invalid amount. Please enter a whole number.")
        return time()

    # Validate the withdrawal amount
    if amount <= 0:
        print("Withdrawal amount must be greater than zero.")
        return time()

    # Ensure the amount is divisible by $5
    if amount % 5 != 0:
        print("Withdrawal amount must be a multiple of $5.")
        return time()

    # Check if the customer has enough balance
    if amount > balance:
        print("Insufficient funds. Your balance is too low.")
        return time()

    # Check if the amount exceeds the remaining daily limit
    if amount > remaining_limit:
        print(f"Amount exceeds your remaining daily limit of ${remaining_limit:,.2f}.")
        return time()

    if time() - start_time > 30:
        return time()

    # Ask the customer to select bill denominations
    print("\nSelect your bill denominations by entering the quantity of each:")
    print("Available bills: $20, $10, and $5")

    try:
        bills_20 = int(input("Number of $20 bills: "))
        bills_10 = int(input("Number of $10 bills: "))
        bills_5 = int(input("Number of $5 bills: "))
    except ValueError:
        print("Invalid quantity. Please enter whole numbers only.")
        return time()

    if time() - start_time > 30:
        return time()

    # Make sure bill quantities are not negative
    if min(bills_20, bills_10, bills_5) < 0:
        print("Bill quantities cannot be negative.")
        return time()

    # Calculate the total value of the selected bills
    selected_total = (
        bills_20 * 20 +
        bills_10 * 10 +
        bills_5 * 5
    )

    # Check if the selected bills match the withdrawal amount
    if selected_total != amount:
        print(f"The selected bills total ${selected_total:,.2f}, not ${amount:,.2f}.")
        print("Withdrawal cancelled. Please try again.")
        return time()
    
    # Check if the ATM has enough bills
    if not cash_handler.check_cash_available(cursor, bills_20, bills_10, bills_5):
        print("Withdrawal cancelled. ATM does not have enough cash.")
        return time()
    
    # Display the withdrawal summary
    print("\n===== WITHDRAWAL SUMMARY =====")
    print(f"Withdrawal amount: ${amount:,.2f}")
    print(f"$20 bills: {bills_20}")
    print(f"$10 bills: {bills_10}")
    print(f"$5 bills:  {bills_5}")
    print(f"New balance: ${balance - amount:,.2f}")

    # Ask the customer to confirm the withdrawal
    confirm = input("\nConfirm withdrawal? (Y/N): ").strip().upper()

    if time() - start_time > 30:
        return time()

    # Cancel the transaction if the customer does not confirm
    if confirm != "Y":
        print("Withdrawal cancelled. Your balance has not changed.")
        return time()

    # Recheck the balance and daily limit before processing
    cursor.execute(
        "SELECT balance, withdraw_limit FROM atm WHERE pin_number = ?",
        (account_id,)
    )
    current_account = cursor.fetchone()

    if current_account is None:
        print("Account not found. Withdrawal cancelled.")
        return time()

    current_balance, current_daily_limit = current_account

    # Get the latest total withdrawals for today
    cursor.execute(
        """SELECT COALESCE(SUM(amount), 0)
           FROM withdrawal_transactions
           WHERE pin_number = ? AND transaction_date = ?""",
        (account_id, today)
    )
    current_withdrawn_today = cursor.fetchone()[0]

    # Make sure the transaction is still valid
    if (amount > current_balance or
            current_withdrawn_today + amount > current_daily_limit):
        print("The account balance or daily limit changed. Please try again.")
        return time()
    
    # Check ATM cash again before completing the withdrawal
    if not cash_handler.check_cash_available(cursor, bills_20, bills_10, bills_5):
        print("Withdrawal cancelled. ATM cash inventory has changed.")
        return time()

    # Deduct the withdrawal amount from the account balance
    cursor.execute(
        "UPDATE atm SET balance = balance - ? WHERE pin_number = ?",
        (amount, account_id)
    )

    # Deduct the bills from ATM cash inventory
    cash_handler.deduct_cash(cursor, bills_20, bills_10, bills_5)
    
    # Save the withdrawal details in the transaction history
    cursor.execute(
        """INSERT INTO withdrawal_transactions
           (pin_number, amount, bills_20, bills_10, bills_5, transaction_date)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (account_id, amount, bills_20, bills_10, bills_5, today)
    )

    # Display the successful transaction message
    print("\nWithdrawal successful!")
    print(f"Your new balance is: ${current_balance - amount:,.2f}")

    return time()