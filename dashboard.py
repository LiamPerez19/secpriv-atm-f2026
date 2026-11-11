def show_dashboard():

    print("\n" + "=" * 40)
    print("             ATM SYSTEM")
    print("=" * 40)
    print("1. View Account Balance")
    print("2. View Withdrawal & Transfer Limits")
    print("3. Withdraw Funds")
    print("4. Deposit Funds")
    print("5. Transfer Funds")
    print("6. Exit")
    print("=" * 40)

    while True:
        choice = input("Please select an option : ")

        if choice in ["1", "2", "3", "4", "5", "6"]:
            return choice
        else:
            print("Invalid option. Please select a number from 1 to 6.")