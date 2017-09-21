DROP DATABASE IF EXISTS StoreManage;
CREATE DATABASE StoreManage;
USE StoreManage;

CREATE TABLE PhoneNumbers(
    phone_id MEDIUMINT NOT NULL
    AUTO_INCREMENT,
    phone_number CHAR(11) NOT NULL,
    PRIMARY KEY (phone_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE Providers(
    pid MEDIUMINT NOT NULL AUTO_INCREMENT,
    name VARCHAR (30) NOT NULL,
    addr VARCHAR (30) NOT NULL,
    PRIMARY KEY (pid)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
CREATE TABLE ProviderPhones(
    pid MEDIUMINT NOT NULL,
    phone_id MEDIUMINT NOT NULL,
    PRIMARY KEY (pid, phone_id),
    FOREIGN KEY (pid) REFERENCES Providers(pid),
    FOREIGN KEY (phone_id) REFERENCES PhoneNumbers(phone_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE Clients(
    cid MEDIUMINT NOT NULL AUTO_INCREMENT,
    name VARCHAR(30) NOT NULL,
    nickname VARCHAR(10) NOT NULL,
    email VARCHAR(30) NOT NULL,
    addr VARCHAR(30) NOT NULL,
    pw CHAR(128) NOT NULL,
    PRIMARY KEY(cid)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
CREATE TABLE ClientPhones(
    cid MEDIUMINT NOT NULL,
    phone_id MEDIUMINT NOT NULL,
    PRIMARY KEY (cid, phone_id),
    FOREIGN KEY (cid) REFERENCES Clients(cid),
    FOREIGN KEY (phone_id) REFERENCES PhoneNumbers(phone_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE Types(
    tid MEDIUMINT NOT NULL AUTO_INCREMENT,
    name VARCHAR(30) NOT NULL,
    parent MEDIUMINT,
    PRIMARY KEY(tid),
    FOREIGN KEY(parent) REFERENCES Types(tid)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
CREATE TABLE Goods(
    gid MEDIUMINT NOT NULL AUTO_INCREMENT,
    name VARCHAR(30) NOT NULL,
    tid MEDIUMINT NOT NULL,
    price FLOAT NOT NULL,
    PRIMARY KEY (gid),
    FOREIGN KEY (tid) REFERENCES Types(tid)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE Employees(
    eid MEDIUMINT NOT NULL AUTO_INCREMENT,
    name VARCHAR(10) NOT NULL,
    sex CHAR(1) NOT NULL,
    email VARCHAR(30) NOT NULL,
    nickname VARCHAR(10) NOT NULL,
    pw CHAR(128) NOT NULL,
    addr VARCHAR(30) NOT NULL,
    birthday DATE NOT NULL,
    isSU BOOLEAN NOT NULL,
    PRIMARY KEY (eid)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
CREATE TABLE EmployeePhones(
    eid MEDIUMINT NOT NULL,
    phone_id MEDIUMINT NOT NULL,
    PRIMARY KEY (eid, phone_id),
    FOREIGN KEY (phone_id) REFERENCES PhoneNumbers(phone_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE Warehouses(
    wid MEDIUMINT NOT NULL AUTO_INCREMENT,
    name VARCHAR(15) NOT NULL,
    addr VARCHAR(30) NOT NULL,
    PRIMARY KEY (wid)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE Orders(
    oid MEDIUMINT NOT NULL AUTO_INCREMENT,
    cid MEDIUMINT NOT NULL,
    time TIMESTAMP NOT NULL,
    state VARCHAR(10) NOT NULL,
    PRIMARY KEY (oid),
    FOREIGN KEY (cid) REFERENCES Clients(cid)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE OrderDetails(
    oid MEDIUMINT NOT NULL,
    gid MEDIUMINT NOT NULL,
    count INT NOT NULL,
    price FLOAT NOT NULL,
    PRIMARY KEY (oid, gid),
    FOREIGN KEY (oid) REFERENCES Orders(oid),
    FOREIGN KEY (gid) REFERENCES Goods(gid)
)
ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE Provide(
    pid MEDIUMINT NOT NULL,
    gid MEDIUMINT NOT NULL,
    price FLOAT NOT NULL,
    PRIMARY KEY (pid, gid),
    FOREIGN KEY (pid) REFERENCES Providers(pid),
    FOREIGN KEY (gid) REFERENCES Goods(gid)
)
ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE Store(
    wid MEDIUMINT NOT NULL,
    gid MEDIUMINT NOT NULL,
    count INT NOT NULL,
    min INT NOT NULL,
    max INT NOT NULL,
    PRIMARY KEY (wid, gid),
    FOREIGN KEY (wid) REFERENCES Warehouses(wid),
    FOREIGN KEY (gid) REFERENCES Goods(gid)
)
ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE StockIn(
    siid MEDIUMINT NOT NULL AUTO_INCREMENT,
    wid MEDIUMINT NOT NULL,
    gid MEDIUMINT NOT NULL,
    eid MEDIUMINT NOT NULL,
    count INT NOT NULL,
    time TIMESTAMP NOT NULL,
    reason VARCHAR(30) NOT NULL,
    extra MEDIUMINT NOT NULL,
    PRIMARY KEY (siid),
    FOREIGN KEY (wid) REFERENCES Warehouses(wid),
    FOREIGN KEY (gid) REFERENCES Goods(gid),
    FOREIGN KEY (eid) REFERENCES Employees(eid)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE StockOut(
    soid MEDIUMINT NOT NULL AUTO_INCREMENT,
    wid MEDIUMINT NOT NULL,
    gid MEDIUMINT NOT NULL,
    eid MEDIUMINT NOT NULL,
    count INT NOT NULL,
    time TIMESTAMP NOT NULL,
    reason VARCHAR(30) NOT NULL,
    extra MEDIUMINT NOT NULL,
    PRIMARY KEY (soid),
    FOREIGN KEY (wid) REFERENCES Warehouses(wid),
    FOREIGN KEY (gid) REFERENCES Goods(gid),
    FOREIGN KEY (eid) REFERENCES Employees(eid)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE OperationHistories
(
    history_id INT NOT NULL AUTO_INCREMENT,
    eid MEDIUMINT NOT NULL,
    time TIMESTAMP NOT NULL,
    table_name VARCHAR(15) NOT NULL,
    operation CHAR(6) NOT NULL,
    statement TINYTEXT NOT NULL,
    PRIMARY KEY (history_id),
    FOREIGN KEY (eid) REFERENCES Employees(eid)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE Manage(
    eid MEDIUMINT NOT NULL,
    wid MEDIUMINT NOT NULL,
    PRIMARY KEY (eid, wid),
    FOREIGN KEY (eid) REFERENCES Employees(eid),
    FOREIGN KEY (wid) REFERENCES Warehouses(wid)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE Schedule
(
    sid MEDIUMINT NOT NULL AUTO_INCREMENT,
    eid MEDIUMINT NOT NULL,
    checker MEDIUMINT,
    source MEDIUMINT NOT NULL,
    target MEDIUMINT NOT NULL,
    time TIMESTAMP NOT NULL,
    PRIMARY KEY (sid),
    FOREIGN KEY (eid) REFERENCES Employees(eid),
    FOREIGN KEY (checker) REFERENCES Employees(eid),
    FOREIGN KEY (source) REFERENCES Warehouses(wid),
    FOREIGN KEY (target) REFERENCES Warehouses(wid)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE ScheduleDetail(
    sid MEDIUMINT NOT NULL,
    gid MEDIUMINT NOT NULL,
    count INT NOT NULL,
    state VARCHAR(10) NOT NULL,
    PRIMARY KEY (sid, gid),
    FOREIGN KEY (sid) REFERENCES Schedule(sid),
    FOREIGN KEY (gid) REFERENCES Goods(gid)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE Purchase(
    purchase_id MEDIUMINT NOT NULL AUTO_INCREMENT,
    pid MEDIUMINT NOT NULL,
    eid MEDIUMINT NOT NULL,
    checker MEDIUMINT,
    wid MEDIUMINT NOT NULL,
    time TIMESTAMP NOT NULL,
    PRIMARY KEY (purchase_id),
    FOREIGN KEY (pid) REFERENCES Providers(pid),
    FOREIGN KEY (eid) REFERENCES Employees(eid),
    FOREIGN KEY (checker) REFERENCES Employees(eid),
    FOREIGN KEY (wid) REFERENCES Warehouses(wid)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE PurchaseDetail(
    purchase_id MEDIUMINT NOT NULL,
    gid MEDIUMINT NOT NULL,
    price FLOAT NOT NULL,
    state VARCHAR(10) NOT NULL,
    PRIMARY KEY (purchase_id, gid),
    FOREIGN KEY (gid) REFERENCES Goods(gid)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE Breakage(
    bid MEDIUMINT NOT NULL AUTO_INCREMENT,
    eid MEDIUMINT NOT NULL,
    checker MEDIUMINT,
    wid MEDIUMINT NOT NULL,
    time TIMESTAMP NOT NULL,
    PRIMARY KEY (bid),
    FOREIGN KEY (eid) REFERENCES Employees(eid),
    FOREIGN KEY (checker) REFERENCES Employees(eid),
    FOREIGN KEY (wid) REFERENCES Warehouses(wid)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE BreakageDetail(
    bid MEDIUMINT NOT NULL,
    gid MEDIUMINT NOT NULL,
    count INT NOT NULL,
    price FLOAT NOT NULL,
    state VARCHAR(10) NOT NULL,
    PRIMARY KEY (bid, gid),
    FOREIGN KEY (bid) REFERENCES Breakage(bid),
    FOREIGN KEY (gid) REFERENCES Goods(gid)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;