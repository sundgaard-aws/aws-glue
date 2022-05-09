create table cpty (
    cpty_id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
    short_name varchar(30),
    full_name varchar(100),
    external_id varchar(50),
    region varchar(20)
);

insert into cpty values(null, 'COMP_A', 'COMPANY A', 'F-312331', 'EUROPE');
insert into cpty values(null, 'COMP_B', 'COMPANY B', 'IOA-90005', 'US');
insert into cpty values(null, 'COMP_F', 'COMPANY F', 'PLJJH-22-KRTT', 'AFRICA');
insert into cpty values(null, 'COMP_G', 'COMPANY G', 'F-222322', 'EUROPE');