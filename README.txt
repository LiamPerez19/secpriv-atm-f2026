-- STRUCTURE OF CODE --

runner.py - the main state machine that will handle all the rest of the code.

ALL other functions (login, admin, etc) should be their own separate files (one person's code per file) - runner will handle them all together.

Runner creates a "cursor" object that runs SQL commands and stores the output - pass the cursor as a parameter to your functions

-- DATABASE INFO --

Name of database is "atm" eg. "SELECT * FROM atm"

db file is named users.db

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