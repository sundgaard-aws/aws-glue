create table trade3 (
    trade_id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
    trade_type varchar(30),
    trade_amount decimal,
    trade_ccy varchar(3),
    trade_date datetime,
    trader_id int,
    counterparty_id int
);