create table counterparty (
    counterpartyid int PRIMARY KEY NOT NULL AUTO_INCREMENT,
    shortname varchar(30),
    fullname varchar(100),
    extid varchar(50)
);