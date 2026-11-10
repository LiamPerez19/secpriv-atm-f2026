from time import sleep
import hashlib

def test(cursor):
        
    #test to see if everything can be grabbed (it works)
        cursor.execute("SELECT * FROM atm ORDER BY username")
        rows = cursor.fetchall()
        for row in rows:
            print(row)

def login_logic(cursor):
    attempts = 0
    trying = True
    valid = True
    id = ""
    dob = ""

    while trying:

        #force timeout after 3 failed logins
        if attempts == 3:
            print("Too many failed logins - try again in 1 minute")
            sleep(60)
            attempts = -1

        #take in both PIN and DOB for login purposes
        id = str(input("Please enter your PIN number (8 digits, numeric characters only): "))
        dob = str(input("Please enter your date of birth (10 characters, MM/DD/YYYY): "))

        #check that the ID and DOB entered are valid
        if not id.isdigit() or len(id) != 8:
            print("Invalid PIN input")
            valid = False

        if len(dob) != 10 or dob[2] != '/' or dob[5] != '/':
            print("Invalid DOB input")
            valid = False

        #if they are, look up all entries in the database with that ID/DOB combination via prepared statement
        if valid:
            salted_id = dob + id
            hashed_id = (hashlib.sha256(salted_id.encode())).hexdigest()
            cursor.execute("SELECT * FROM atm WHERE pin_number = ?", (hashed_id,))
            rows = cursor.fetchall()
            i = 0

            #check if a valid user was found: if this is so, exit the while loop, as we've found our user
            for row in rows:
                i += 1
            if i > 0:
                trying = False
            else:
                print("Failed to find valid user - incorrect PIN or DOB")

        #every loop, restart the validation check and increment attempts
        attempts += 1
        valid = True

    return hashed_id