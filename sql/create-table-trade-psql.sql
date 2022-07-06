create table trade (
    trade_id int PRIMARY KEY NOT NULL GENERATED ALWAYS AS IDENTITY,
    trade_type varchar(30),
    trade_amount decimal,
    trade_ccy varchar(3),
    trade_date timestamp,
    trader_id int,
    counterparty_id int
);