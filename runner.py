import sqlite3
import login

def main():

    #initialize connection and cursor
    connection = sqlite3.connect("users2.db")
    cursor = connection.cursor()
    print("Database connected successfully + cursor initialized successfully")

    id = str(login.login_logic(cursor))

    cursor.execute("SELECT username FROM atm WHERE pin_number = ?", (id,))
    username = cursor.fetchone()[0]
    print(f"Welcome, user {username}")

    #end run
    connection.close()
    return 1

if __name__ == "__main__":
    main()