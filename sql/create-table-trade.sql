create table trade (
    trade_id int NOT NULL AUTO_INCREMENT,
    trade_type varchar(30),
    trade_amount decimal,
    trade_ccy varchar(3),
    trade_date datetime,
    trader_id int,
    counterparty_id int
)

insert into trade values(null, 'FXSPOT', 500000, 'USD', now(), 5, null);
insert into trade values(null, 'FXSPOT', 1500000, 'EUR', now(), 5, null);
insert into trade values(null, 'FXSPOT', 2000000, 'DKK', now(), 5, null);