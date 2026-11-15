import sqlite3
import login
import dashboard
import withdraw
import deposit
import transfer
import admin
import cash_handler

def main():

    #initialize connection and cursor
    connection = sqlite3.connect("users2.db")
    cursor = connection.cursor()
    print("Database connected successfully + cursor initialized successfully")

    admin.init_admin_table(cursor)
    connection.commit()

    cash_handler.setup_handler_table(cursor)
    cash_handler.setup_cash_table(cursor)
    connection.commit()

    print("\n" + "=" * 40)
    print("         WELCOME TO ATM SYSTEM")
    print("=" * 40)
    entry = input("Press Enter to begin ")

    # Cash Handler login
    if entry == "ATMCASH":
        handler_id = cash_handler.cash_handler_login(cursor)
        if handler_id:
            cash_handler.cash_handler_menu(cursor, handler_id)
        connection.close()
        return 0

    # Hidden admin gateway: exits completely if admin authentication fails
    if admin.check_gateway_code(entry):
        admin_id = admin.admin_login(cursor)
        if admin_id:
            admin.admin_menu(cursor, connection, admin_id)
        connection.close()
        return 0

    id = str(login.login_logic(cursor))

    cursor.execute("SELECT username FROM atm WHERE pin_number = ?", (id,))
    username = cursor.fetchone()[0]
    print(f"Welcome, user {username}")

    while True:
        choice = dashboard.show_dashboard()
        

        # 1. View Account Balance
        if choice == "1":
            cursor.execute(
                "SELECT balance FROM atm WHERE pin_number = ?",
                (id,)
            )
            result = cursor.fetchone()

            if result:
                print(f"\nYour available account balance is: ${result[0]:,.2f}")
            else:
                print("No account balance found.")

        # 2. View Withdrawal & Transfer Limits
        elif choice == "2":
            cursor.execute(
                "SELECT withdraw_limit FROM atm WHERE pin_number = ?",
                (id,)
            )
            result = cursor.fetchone()

            cursor.execute(
                "SELECT deposit_limit FROM atm WHERE pin_number = ?",
                (id,)
            )
            result2 = cursor.fetchone()

            if result and result2:
                print("\n===== ACCOUNT LIMITS =====")
                print(f"Daily Withdrawal Limit: ${result[0]:,.2f}")
                print(f"Daily Deposit Limit: ${result2[0]:,.2f}")

        # 3. Withdraw Funds
        elif choice == "3":
            withdraw.withdraw_money(cursor, id)
            connection.commit()

        # 4. Deposit Funds
        elif choice == "4":
            deposit.deposit_money(cursor, id)
            connection.commit()

        # 5. Transfer Funds
        elif choice == "5":
            transfer.transfer_funds(cursor, id)
            connection.commit()

        # 6. Exit
        elif choice == "6":
            print("\nThank you for using ATM SYSTEM. Goodbye!")
            break

    #end run
    connection.close()
    return 1

if __name__ == "__main__":
    main()
