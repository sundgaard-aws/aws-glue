drop table danish_trade_partitioned;
create table danish_trade_partitioned (
    trade_id int NOT NULL GENERATED ALWAYS AS IDENTITY,
    trade_type varchar(30),
    trade_amount decimal,
    trade_ccy varchar(3),
    trade_date timestamp,
    trader_id int,
    counterparty_id int
) partition by list (trade_ccy);

CREATE TABLE danish_trade_partitioned_dkk PARTITION OF danish_trade_partitioned FOR VALUES IN ('DKK');
CREATE TABLE danish_trade_partitioned_usd PARTITION OF danish_trade_partitioned FOR VALUES IN ('USD');
CREATE TABLE danish_trade_partitioned_sek PARTITION OF danish_trade_partitioned FOR VALUES IN ('SEK');
CREATE TABLE danish_trade_partitioned_eur PARTITION OF danish_trade_partitioned FOR VALUES IN ('EUR');
CREATE TABLE danish_trade_partitioned_gbp PARTITION OF danish_trade_partitioned FOR VALUES IN ('GBP');

insert into danish_trade_partitioned(trade_ccy,trade_amount,trade_type,trade_date) values('DKK',100000,'FXSPOT',now());
truncate table danish_trade_partitioned;