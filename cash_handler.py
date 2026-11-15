import hashlib
import hmac
MAX_CASH = 10000

def setup_handler_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cash_handlers (
            handler_pin TEXT PRIMARY KEY,
            date_of_birth TEXT NOT NULL,
            handler_name TEXT NOT NULL
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM cash_handlers")
    if cursor.fetchone()[0] == 0:
        pin = "88776655"
        dob = "01/01/2000"
        hashed_pin = hashlib.sha256((dob + pin).encode()).hexdigest()

        cursor.execute(
            "INSERT INTO cash_handlers (handler_pin, date_of_birth, handler_name) VALUES (?, ?, ?)",
            (hashed_pin, dob, "TestHandler")
        )

def cash_handler_login(cursor):
    print("\n===== CASH HANDLER LOGIN =====")

    pin = input("Enter Cash Handler 8-digit PIN: ").strip()
    dob = input("Enter Date of Birth (MM/DD/YYYY): ").strip()

    if not pin.isdigit() or len(pin) != 8 or len(dob) != 10 or dob[2] != "/" or dob[5] != "/":
        print("Invalid PIN or DOB format.")
        return None

    hashed_pin = hashlib.sha256((dob + pin).encode()).hexdigest()

    cursor.execute(
        "SELECT handler_pin, handler_name FROM cash_handlers WHERE handler_pin = ? AND date_of_birth = ?",
        (hashed_pin, dob)
    )

    result = cursor.fetchone()

    if result and hmac.compare_digest(result[0], hashed_pin):
        print(f"Welcome, Cash Handler {result[1]}")
        return hashed_pin

    print("Authentication failed.")
    return None

def setup_cash_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS atm_cash (
            denomination INTEGER PRIMARY KEY,
            quantity INTEGER NOT NULL CHECK(quantity >= 0)
        )
    """)
    cursor.executemany(
        "INSERT OR IGNORE INTO atm_cash (denomination, quantity) VALUES (?, ?)",
        [(20, 0), (10, 0), (5, 0)]
    )

def cash_handler_menu(cursor, handler_id):
    cursor.execute(
        "SELECT handler_pin FROM cash_handlers WHERE handler_pin = ?",
        (handler_id,)
    )
    result = cursor.fetchone()
    if not result or not hmac.compare_digest(result[0], handler_id):
        print("Access denied. Cash Handler login required.")
        return

    while True:
        print("\n===== CASH HANDLER MENU =====")
        print("1. View Cash Inventory")
        print("2. Restock Cash")
        print("3. Remove Cash")
        print("4. Logout")

        choice = input("Select an option: ")

        if choice == "1":
            view_cash_inventory(cursor)

        elif choice == "2":
            restock_cash(cursor)

        elif choice == "3":
            remove_cash(cursor)

        elif choice == "4":
            print("Logging out...")
            break

        else:
            print("Invalid option. Please try again.")

def view_cash_inventory(cursor):
    cursor.execute("SELECT denomination, quantity FROM atm_cash ORDER BY denomination DESC")
    rows = cursor.fetchall()

    print("\n===== CASH INVENTORY =====")
    total = 0

    for denomination, quantity in rows:
        print(f"${denomination} bills: {quantity}")
        total += denomination * quantity

    print(f"Total cash: ${total:,.2f}")

def restock_cash(cursor):
    print("\n===== RESTOCK CASH =====")

    try:
        bills_20 = int(input("Number of $20 bills: "))
        bills_10 = int(input("Number of $10 bills: "))
        bills_5 = int(input("Number of $5 bills: "))
    except ValueError:
        print("Invalid input. Please enter whole numbers.")
        return

    if min(bills_20, bills_10, bills_5) < 0:
        print("Bill quantities cannot be negative.")
        return

    if bills_20 + bills_10 + bills_5 == 0:
        print("No cash added.")
        return

    # Get the current cash total
    cursor.execute("SELECT denomination, quantity FROM atm_cash")
    rows = cursor.fetchall()

    current_total = 0
    for denomination, quantity in rows:
        current_total += denomination * quantity

    # Calculate the amount being added
    added_cash = bills_20 * 20 + bills_10 * 10 + bills_5 * 5

    if current_total + added_cash > MAX_CASH:
        print(f"Cash capacity exceeded. Maximum is ${MAX_CASH:,}.")
        return

    for denomination, quantity in [(20, bills_20), (10, bills_10), (5, bills_5)]:
        cursor.execute(
            "UPDATE atm_cash SET quantity = quantity + ? WHERE denomination = ?",
            (quantity, denomination)
        )

    cursor.connection.commit()
    print("Cash restocked successfully!")

def remove_cash(cursor):
    print("\n===== REMOVE CASH =====")

    try:
        bills_20 = int(input("Number of $20 bills to remove: "))
        bills_10 = int(input("Number of $10 bills to remove: "))
        bills_5 = int(input("Number of $5 bills to remove: "))
    except ValueError:
        print("Invalid input. Please enter whole numbers.")
        return

    if min(bills_20, bills_10, bills_5) < 0:
        print("Bill quantities cannot be negative.")
        return

    if bills_20 + bills_10 + bills_5 == 0:
        print("No cash removed.")
        return

    bills = [(20, bills_20), (10, bills_10), (5, bills_5)]

    for denomination, quantity in bills:
        cursor.execute(
            "SELECT quantity FROM atm_cash WHERE denomination = ?",
            (denomination,)
        )
        result = cursor.fetchone()

        if result is None or quantity > result[0]:
            print(f"Not enough ${denomination} bills available.")
            return

    for denomination, quantity in bills:
        cursor.execute(
            "UPDATE atm_cash SET quantity = quantity - ? WHERE denomination = ?",
            (quantity, denomination)
        )

    cursor.connection.commit()
    print("Cash removed successfully!")

def check_cash_available(cursor, bills_20, bills_10, bills_5):
    bills = [(20, bills_20), (10, bills_10), (5, bills_5)]

    for denomination, quantity in bills:
        cursor.execute(
            "SELECT quantity FROM atm_cash WHERE denomination = ?",
            (denomination,)
        )
        result = cursor.fetchone()

        if result is None or quantity > result[0]:
            print(f"Not enough ${denomination} bills available.")
            return False

    return True

def deduct_cash(cursor, bills_20, bills_10, bills_5):
    bills = [(20, bills_20), (10, bills_10), (5, bills_5)]

    # Deduct bills from ATM inventory
    for denomination, quantity in bills:
        cursor.execute(
            "UPDATE atm_cash SET quantity = quantity - ? WHERE denomination = ?",
            (quantity, denomination)
        )
