-- STRUCTURE OF CODE --

runner.py - the main state machine that will handle all the rest of the code.

ALL other functions (login, admin, etc) should be their own separate files (one person's code per file) - runner will handle them all together.

Runner creates a "cursor" object that runs SQL commands and stores the output - pass the cursor as a parameter to your functions

-- DATABASE INFO --

Name of database is "atm" eg. "SELECT * FROM atm"

db file is named users.db

-- ADDED NOTE ON PREPARED STATEMENTS --

Prepared statements are formatted like 

cursor.execute("SELECT username FROM atm WHERE pin_number = ?", (id,))

Comma is necessary for the code to recognize it as a list and not a statement 

For multiple inputs, 

cursor.execute("SELECT username FROM atm WHERE pin_number = ? AND dob = ?", (id,dob))

No appending comma required

Fields: 
- pin_number (currently 8-character string filling in for 8-digit number, hashing to be added)
- date_of_birth (10-char string of format "MM/DD/YYYY")
- username (string of at most 30 characters)
- balance (int)
- withdraw_limit (int)
- deposit_limit (int)

-- TODO -- 

DATABASE / LOGIN
- replace ID numbers stored in database with hashed versions / add hashing to ID input