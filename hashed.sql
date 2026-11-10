CREATE TABLE atm(
    pin_number char(64)  NOT NULL, --64 bit hash string of password+salt (dob is salt)
    date_of_birth char(10) NOT NULL, --stored as "XX/YY/ZZZZ" month/day/year
    username varchar(30) NOT NULL, --displayed on successful login - not used as a login parameter
    balance int  NOT NULL,
    withdraw_limit int NOT NULL,
    deposit_limit int NOT NULL,
    CONSTRAINT atm_pk PRIMARY KEY (pin_number)
);

--passwords: alice 12233344, bob 44555556, mallory 66666777, samy 77778899

INSERT INTO atm (pin_number, date_of_birth, username, balance, withdraw_limit, deposit_limit) VALUES ('8f5e8bfd4dfad49f705261dfb950f1e5082baafefc573b5a86be6576d7114cf0','01/02/2003','alice',50000,5000,5000);
INSERT INTO atm (pin_number, date_of_birth, username, balance, withdraw_limit, deposit_limit) VALUES ('0a4a3c5cc720664cec50d722e9b483a3c292d23500fdfe66f60df244baf6186e','03/04/1999','bob',300000,20000,4000);
INSERT INTO atm (pin_number, date_of_birth, username, balance, withdraw_limit, deposit_limit) VALUES ('8871e290ca844be7150ee5e03b28eeedafc4ca953b3de8f7173896cf61325474','11/12/1984','mallory',2500,100,6000);
INSERT INTO atm (pin_number, date_of_birth, username, balance, withdraw_limit, deposit_limit) VALUES ('c8bf05b31a69932b5dee3b1eebba3d856a9cad1fa1c4991d9395b420d69f5130','09/05/2000','samy',0,500,7000);