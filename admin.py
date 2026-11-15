from time import sleep
import hashlib
import hmac
import sqlite3

# SHA-256 hash of secret gateway code: "ATMADMIN"
GATEWAY_CODE_HASH = hashlib.sha256(b"ATMADMIN").hexdigest()


def init_admin_table(cursor):
    """Creates the isolated admins table and seeds one default admin if empty."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            admin_pin CHAR(64) NOT NULL PRIMARY KEY,
            date_of_birth CHAR(10) NOT NULL,
            admin_name VARCHAR(30) NOT NULL
        )
    """)

    # Default Admin -> PIN: 99887766 | DOB: 01/01/2000
    cursor.execute("SELECT COUNT(*) FROM admins")
    if cursor.fetchone()[0] == 0:
        default_hash = hashlib.sha256(("01/01/2000" + "99887766").encode()).hexdigest()
        cursor.execute(
            "INSERT INTO admins (admin_pin, date_of_birth, admin_name) VALUES (?, ?, ?)",
            (default_hash, "01/01/2000", "SystemAdmin")
        )


def check_gateway_code(user_input):
    """Constant-time check for the hidden admin gateway code."""
    candidate_hash = hashlib.sha256(user_input.strip().encode()).hexdigest()
    return hmac.compare_digest(candidate_hash, GATEWAY_CODE_HASH)


def is_authorized_admin(cursor, admin_pin):
    """Verifies that the active session hash exists in the admins table."""
    if not admin_pin or len(admin_pin) != 64:
        return False
    cursor.execute("SELECT admin_pin FROM admins WHERE admin_pin = ?", (admin_pin,))
    row = cursor.fetchone()
    return row is not None and hmac.compare_digest(row[0], admin_pin)


def admin_login(cursor):
    """Single-attempt admin login; immediately exits on any invalid input or failed match."""
    init_admin_table(cursor)
    print("\n" + "=" * 40)
    print("      RESTRICTED ADMINISTRATOR LOGIN")
    print("=" * 40)

    pin = input("Enter Admin 8-digit PIN: ").strip()
    dob = input("Enter Admin Date of Birth (MM/DD/YYYY): ").strip()

    if not pin.isdigit() or len(pin) != 8 or len(dob) != 10 or dob[2] != '/' or dob[5] != '/':
        print("Authentication failed. Exiting.")
        sleep(600)
        return None

    hashed_id = hashlib.sha256((dob + pin).encode()).hexdigest()
    cursor.execute(
        "SELECT admin_pin, admin_name FROM admins WHERE admin_pin = ? AND date_of_birth = ?",
        (hashed_id, dob)
    )
    row = cursor.fetchone()

    if row and hmac.compare_digest(row[0], hashed_id):
        print(f"\nAuthenticated as Administrator: {row[1]}")
        return hashed_id

    print("Authentication failed. Exiting.")
    sleep(600)
    return None


def lookup_customer(cursor):
    """Prompts for a customer's PIN and DOB and returns their row from 'atm'."""
    pin = input("Enter customer 8-digit PIN: ").strip()
    dob = input("Enter customer Date of Birth (MM/DD/YYYY): ").strip()

    if not pin.isdigit() or len(pin) != 8 or len(dob) != 10 or dob[2] != '/' or dob[5] != '/':
        print("Invalid PIN or DOB format.")
        return None

    hashed_id = hashlib.sha256((dob + pin).encode()).hexdigest()
    cursor.execute(
        """SELECT pin_number, username, date_of_birth, balance, withdraw_limit, deposit_limit
           FROM atm WHERE pin_number = ?""",
        (hashed_id,)
    )
    account = cursor.fetchone()
    if account is None:
        print("No matching customer account found.")
        return None
    return account


def create_account(cursor, admin_pin):
    """Creates a new customer account in 'atm'."""
    if not is_authorized_admin(cursor, admin_pin):
        print("ACCESS DENIED: Administrator privileges required.")
        return

    print("\n===== CREATE NEW CUSTOMER ACCOUNT =====")
    username = input("Enter customer full name (max 30 chars): ").strip()
    dob = input("Enter Date of Birth (MM/DD/YYYY): ").strip()
    pin = input("Enter 8-digit numeric PIN: ").strip()
    balance_str = input("Enter starting balance ($): ").strip()
    w_limit_str = input("Enter daily withdrawal limit ($): ").strip()
    d_limit_str = input("Enter daily deposit limit ($): ").strip()

    if not (1 <= len(username) <= 30):
        print("Invalid name. Must be 1 to 30 characters.")
        return
    if len(dob) != 10 or dob[2] != '/' or dob[5] != '/':
        print("Invalid DOB format. Must be MM/DD/YYYY.")
        return
    if not pin.isdigit() or len(pin) != 8:
        print("Invalid PIN. Must be 8 numeric digits.")
        return
    if not balance_str.isdigit():
        print("Invalid balance. Must be a non-negative whole number.")
        return
    if not (w_limit_str.isdigit() and d_limit_str.isdigit()):
        print("Invalid limits. Daily withdrawal and deposit limits must be non-negative whole numbers.")
        return

    hashed_id = hashlib.sha256((dob + pin).encode()).hexdigest()

    try:
        cursor.execute(
            """INSERT INTO atm (pin_number, date_of_birth, username, balance, withdraw_limit, deposit_limit)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (hashed_id, dob, username, int(balance_str), int(w_limit_str), int(d_limit_str))
        )
        print(f"Customer account for '{username}' created successfully!")
    except sqlite3.IntegrityError:
        print("Error: An account with this PIN and DOB combination already exists.")


def view_customer_account(cursor, admin_pin):
    """Displays balance and limits for a specific customer account."""
    if not is_authorized_admin(cursor, admin_pin):
        print("ACCESS DENIED: Administrator privileges required.")
        return

    print("\n===== VIEW CUSTOMER ACCOUNT STANDINGS =====")
    account = lookup_customer(cursor)
    if account is None:
        return

    _, username, dob, balance, w_limit, d_limit = account
    print(f"\nAccount Holder:         {username}")
    print(f"Date of Birth:          {dob}")
    print(f"Current Balance:        ${balance:,.2f}")
    print(f"Daily Withdrawal Limit: ${w_limit:,.2f}")
    print(f"Daily Deposit Limit:    ${d_limit:,.2f}")


def set_limits(cursor, admin_pin):
    """Updates daily withdrawal and deposit limits for one specific customer."""
    if not is_authorized_admin(cursor, admin_pin):
        print("ACCESS DENIED: Administrator privileges required.")
        return

    print("\n===== SET CUSTOMER DAILY LIMITS =====")
    account = lookup_customer(cursor)
    if account is None:
        return

    hashed_id, username, _, _, curr_w, curr_d = account
    print(f"\nAccount: {username}")
    print(f"Current Daily Withdrawal Limit: ${curr_w:,.2f}")
    print(f"Current Daily Deposit Limit:    ${curr_d:,.2f}")

    w_limit = input("\nEnter new daily withdrawal limit ($): ").strip()
    d_limit = input("Enter new daily deposit limit ($): ").strip()

    if not (w_limit.isdigit() and d_limit.isdigit()):
        print("Invalid input. Limits must be non-negative whole numbers.")
        return

    cursor.execute(
        "UPDATE atm SET withdraw_limit = ?, deposit_limit = ? WHERE pin_number = ?",
        (int(w_limit), int(d_limit), hashed_id)
    )
    print(f"Updated limits for '{username}' -> Withdrawal: ${int(w_limit):,.2f}, Deposit: ${int(d_limit):,.2f}")


def view_logs(cursor, admin_pin):
    """Displays all deposit and withdrawal logs."""
    if not is_authorized_admin(cursor, admin_pin):
        print("ACCESS DENIED: Administrator privileges required.")
        return

    print("\n===== DEPOSIT LOGS =====")
    cursor.execute("SELECT * FROM deposit_transactions")
    for row in cursor.fetchall():
        print(row)

    print("\n===== WITHDRAWAL LOGS =====")
    cursor.execute("SELECT * FROM withdrawal_transactions")
    for row in cursor.fetchall():
        print(row)


def admin_menu(cursor, connection, admin_pin):
    """Protected CLI menu for authenticated administrators."""
    if not is_authorized_admin(cursor, admin_pin):
        print("ACCESS DENIED: Invalid or missing administrator session.")
        return

    while True:
        print("\n=== ADMINISTRATOR MENU ===")
        print("1. Create Customer Account")
        print("2. View Customer Account Standings")
        print("3. Set Customer Daily Limits")
        print("4. View Deposit & Withdrawal Logs")
        print("5. Exit")
        choice = input("Select an option (1-5): ").strip()

        if choice == "1":
            create_account(cursor, admin_pin)
            connection.commit()
        elif choice == "2":
            view_customer_account(cursor, admin_pin)
        elif choice == "3":
            set_limits(cursor, admin_pin)
            connection.commit()
        elif choice == "4":
            view_logs(cursor, admin_pin)
        elif choice == "5":
            print("Logging out of Administrator session.")
            break
        else:
            print("Invalid option. Please select 1-5.")