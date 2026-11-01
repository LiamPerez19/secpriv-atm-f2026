CREATE TABLE atm(
    pin_number char(8)  NOT NULL, --always an 8-digit code
    date_of_birth char(10) NOT NULL, --stored as "XX/YY/ZZZZ" month/day/year
    username varchar(30) NOT NULL, --displayed on successful login - not used as a login parameter
    balance int  NOT NULL,
    withdraw_limit int NOT NULL,
    deposit_limit int NOT NULL,
    CONSTRAINT atm_pk PRIMARY KEY (pin_number)
);

INSERT INTO atm (pin_number, date_of_birth, username, balance, withdraw_limit, deposit_limit) VALUES ('12233344','01/02/2003','alice',50000,5000,5000);
INSERT INTO atm (pin_number, date_of_birth, username, balance, withdraw_limit, deposit_limit) VALUES ('44555556','03/04/1999','bob',300000,20000,4000);
INSERT INTO atm (pin_number, date_of_birth, username, balance, withdraw_limit, deposit_limit) VALUES ('66666777','11/12/1984','mallory',2500,100,6000);
INSERT INTO atm (pin_number, date_of_birth, username, balance, withdraw_limit, deposit_limit) VALUES ('77778899','09/05/2000','samy',0,500,7000);