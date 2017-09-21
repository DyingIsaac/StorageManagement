from app.orm import Model, StringField, IntegerField, FloatField, TextField, DateField, PasswordField, TimestampField
from datetime import date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import login_manager

MEDIUMINT = 'MEDIUMINT'
CHAR11 = 'CHAR(11)'
VARCHAR10 = 'VARCHAR(10)'
VARCHAR15 = 'VARCHAR(15)'
VARCHAR30 = 'VARCHAR(30)'
EMAIL = 'VARCHAR(30)'


def calculate_age(born):
    today = date.today()
    if isinstance(born, str):
        born = date(int(born[:4]), int(born[5:7]), int(born[8:]))
    try:
        birthday = born.replace(year=today.year)
    except ValueError:
        birthday = born.replace(year=today.year, day=born.day-1)
    if birthday > today:
        return today.year - born.year - 1
    else:
        return today.year - born.year


@login_manager.user_loader
def load_user(user_id):
    if user_id[0] == 'c':
        return Client.query.filter_by('cid={}'.format(user_id[1:])).first()
    elif user_id[0] == 'e':
        return Employee.query.filter_by('eid={}'.format(user_id[1:])).first()


class PhoneNumber(Model):
    __table__ = 'PhoneNumbers'

    phone_id = IntegerField(column_name='phone_id', column_type=MEDIUMINT, primary_key=True)
    phone_number = StringField(column_name='phone_number', column_type=CHAR11)

    def __init__(self, phone_id, phone_number):
        super().__init__()
        self.phone_id = phone_id
        self.phone_number = phone_number


class Provider(Model):
    __table__ = 'Providers'

    pid = IntegerField(column_name='pid', column_type=MEDIUMINT, primary_key=True)
    name = StringField(column_name='name', column_type=VARCHAR30)
    addr = StringField(column_name='addr', column_type=VARCHAR30)

    def __init__(self, name, addr, pid=None):
        super().__init__()
        self.pid = pid
        self.name = name
        self.addr = addr


class ProviderPhone(Model):
    __table__ = 'ProviderPhones'

    pid = IntegerField(column_name='pid', column_type=MEDIUMINT, primary_key=True)
    phone_id = IntegerField(column_name='phone_id', column_type=MEDIUMINT, primary_key=True)

    def __init__(self, pid, phone_id):
        super().__init__()
        self.pid = pid
        self.phone_id = phone_id


class Client(Model, UserMixin):
    __table__ = 'Clients'

    cid = IntegerField(column_name='cid', column_type=MEDIUMINT, primary_key=True)
    name = StringField(column_name='name', column_type=VARCHAR30)
    nickname = StringField(column_name='nickname', column_type=VARCHAR10)
    email = StringField(column_name='email', column_type=EMAIL)
    addr = StringField(column_name='addr', column_type=VARCHAR30)
    pw = PasswordField(column_name='pw')

    def __init__(self, name, nickname, email, addr, pw, cid=None):
        super().__init__()
        self.cid = cid
        self.name = name
        self.nickname = nickname
        self.email = email
        self.addr = addr
        self.pw = pw

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.pw = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.pw, password)

    def get_id(self):
        return u'c'+str(self.cid)


class ClientPhone(Model):
    __table__ = 'ClientPhones'

    cid = IntegerField(column_name='cid', column_type=MEDIUMINT, primary_key=True)
    phone_id = IntegerField(column_name='phone_id', column_type=MEDIUMINT, primary_key=True)

    def __init__(self, cid, phone_id):
        super().__init__()
        self.cid = cid
        self.phone_id = phone_id


class Type(Model):
    __table__ = 'Types'

    tid = IntegerField(column_name='tid', column_type=MEDIUMINT, primary_key=True)
    name = StringField(column_name='name', column_type=VARCHAR30)
    parent = IntegerField(column_name='parent', column_type=MEDIUMINT)

    def __init__(self, name, parent, tid=None):
        super().__init__()
        self.tid = tid
        self.name = name
        self.parent = parent


class Good(Model):
    __table__ = 'Goods'

    gid = IntegerField(column_name='gid', column_type=MEDIUMINT, primary_key=True)
    name = StringField(column_name='name', column_type=VARCHAR30)
    tid = IntegerField(column_name='tid', column_type=MEDIUMINT)
    price = FloatField(column_name='price')

    def __init__(self, name, tid, price, gid=None):
        super().__init__()
        self.gid = gid
        self.name = name
        self.tid = tid
        self.price = price


class Employee(Model, UserMixin):
    __table__ = 'Employees'

    eid = IntegerField(column_name='eid', column_type=MEDIUMINT, primary_key=True)
    name = StringField(column_name='name', column_type=VARCHAR10)
    sex = StringField(column_name='sex', column_type='CHAR(1)')
    email = StringField(column_name='email', column_type=EMAIL)
    nickname = StringField(column_name='nickname', column_type=VARCHAR10)
    pw = PasswordField(column_name='pw')
    addr = StringField(column_name='addr', column_type=VARCHAR30)
    birthday = DateField(column_name='birthday')

    def __init__(self, name, sex, email, nickname, pw, addr, birthday, eid=None):
        super().__init__()
        self.eid = eid
        self.name = name
        self.sex = sex
        self.email = email
        self.nickname = nickname
        self.pw = pw
        self.addr = addr
        self.birthday = birthday
        self.age = calculate_age(birthday)

    @property
    def password(self):
        return AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.pw = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.pw, password)

    def get_id(self):
        return u'e'+str(self.eid)


class EmployeePhone(Model):
    __table__ = 'EmployeePhones'

    eid = IntegerField(column_name='eid', column_type=MEDIUMINT, primary_key=True)
    phone_id = IntegerField(column_name='phone_id', column_type=MEDIUMINT, primary_key=True)

    def __init__(self, eid, phone_id):
        super().__init__()
        self.eid = eid
        self.phone_id = phone_id


class Warehouse(Model):
    __table__ = 'Warehouses'

    wid = IntegerField(column_name='wid', column_type=MEDIUMINT, primary_key=True)
    name = StringField(column_name='name', column_type=VARCHAR15)
    addr = StringField(column_name='addr', column_type=VARCHAR30)

    def __init__(self, name, addr, wid=None):
        super().__init__()
        self.wid = wid
        self.name = name
        self.addr = addr


class Order(Model):
    __table__ = 'Orders'

    oid = IntegerField(column_name='oid', column_type=MEDIUMINT, primary_key=True)
    cid = IntegerField(column_name='cid', column_type=MEDIUMINT)
    time = TimestampField(column_name='time')
    state = StringField(column_name='state', column_type=VARCHAR10)

    def __init__(self, cid, time, state, oid=None):
        super().__init__()
        self.oid = oid
        self.cid = cid
        self.time = time
        self.state = state


class OrderDetail(Model):
    __table__ = 'OrderDetails'

    oid = IntegerField(column_name='oid', column_type=MEDIUMINT, primary_key=True)
    gid = IntegerField(column_name='gid', column_type=MEDIUMINT, primary_key=True)
    count = IntegerField(column_name='count')
    price = FloatField(column_name='price')

    def __init__(self, oid, gid, count, price):
        super().__init__()
        self.oid = oid
        self.gid = gid
        self.count = count
        self.price = price


class Provide(Model):
    __table__ = 'Provide'

    pid = IntegerField(column_name='pid', column_type=MEDIUMINT, primary_key=True)
    gid = IntegerField(column_name='gid', column_type=MEDIUMINT, primary_key=True)
    price = FloatField(column_name='price')

    def __init__(self, pid, gid, price):
        super().__init__()
        self.pid = pid
        self.gid = gid
        self.price = price


class Store(Model):
    __table__ = 'Store'

    wid = IntegerField(column_name='wid', column_type=MEDIUMINT, primary_key=True)
    gid = IntegerField(column_name='gid', column_type=MEDIUMINT, primary_key=True)
    count = IntegerField(column_name='count')
    min = IntegerField(column_name='min')
    max = IntegerField(column_name='max')

    def __init__(self, wid, gid, count, min, max):
        super().__init__()
        self.wid = wid
        self.gid = gid
        self.count = count
        self.min = min
        self.max = max


class StockIn(Model):
    __table__ = 'StockIn'

    siid = IntegerField(column_name='siid', column_type=MEDIUMINT, primary_key=True)
    wid = IntegerField(column_name='wid', column_type=MEDIUMINT)
    gid = IntegerField(column_name='gid', column_type=MEDIUMINT)
    eid = IntegerField(column_name='eid', column_type=MEDIUMINT)
    count = IntegerField(column_name='count')
    time = TimestampField(column_name='time')
    reason = StringField(column_name='reason', column_type=VARCHAR30)
    extra = IntegerField(column_name='extra', column_type=MEDIUMINT)

    def __init__(self, wid, gid, eid, count, time, reason, extra, siid=None):
        super().__init__()
        self.siid = siid
        self.wid = wid
        self.gid = gid
        self.eid = eid
        self.count = count
        self.time = time
        self.reason = reason
        self.extra = extra


class StockOut(Model):
    __table__ = 'StockOut'

    soid = IntegerField(column_name='soid', column_type=MEDIUMINT, primary_key=True)
    wid = IntegerField(column_name='wid', column_type=MEDIUMINT)
    gid = IntegerField(column_name='gid', column_type=MEDIUMINT)
    eid = IntegerField(column_name='eid', column_type=MEDIUMINT)
    count = IntegerField(column_name='count')
    time = TimestampField(column_name='time')
    reason = StringField(column_name='reason', column_type=VARCHAR30)
    extra = IntegerField(column_name='extra', column_type=MEDIUMINT)

    def __init__(self, wid, gid, eid, count, time, reason, extra, soid=None):
        super().__init__()
        self.soid = soid
        self.wid = wid
        self.gid = gid
        self.eid = eid
        self.count = count
        self.time = time
        self.reason = reason
        self.extra = extra


class OperationHistory(Model):
    __table__ = 'OperationHistories'

    history_id = IntegerField(column_name='history_id', primary_key=True)
    eid = IntegerField(column_name='eid', column_type=MEDIUMINT)
    time = TimestampField(column_name='time')
    table_name = StringField(column_name='table_name', column_type=VARCHAR15)
    operation = StringField(column_name='operation', column_type='CHAR(6)')
    statement = TextField(column_name='statement', column_type='TINYTEXT')

    def __init__(self, eid, time, table_name, operation, statement, history_id=None):
        super().__init__()
        self.history_id = history_id
        self.eid = eid
        self.tiem = time
        self.table_name = table_name
        self.operation = operation
        self.statement = statement


class Manage(Model):
    __table__ = 'Manage'

    eid = IntegerField(column_name='eid', column_type=MEDIUMINT, primary_key=True)
    wid = IntegerField(column_name='wid', column_type=MEDIUMINT, primary_key=True)

    def __init__(self, eid, wid):
        super().__init__()
        self.eid = eid
        self.wid = wid


class Schedule(Model):
    __table__ = 'Schedule'

    sid = IntegerField(column_name='sid', column_type=MEDIUMINT, primary_key=True)
    eid = IntegerField(column_name='eid', column_type=MEDIUMINT)
    checker = IntegerField(column_name='checker', column_type=MEDIUMINT)
    source = IntegerField(column_name='source', column_type=MEDIUMINT)
    target = IntegerField(column_name='target', column_type=MEDIUMINT)
    time = TimestampField(column_name='time')

    def __init__(self, eid, checker, source, target, time, sid=None):
        super().__init__()
        self.sid = sid
        self.eid = eid
        self.checker = checker
        self.source = source
        self.target = target
        self.time = time


class ScheduleDetail(Model):
    __table__ = 'ScheduleDetail'

    sid = IntegerField(column_name='sid', column_type=MEDIUMINT, primary_key=True)
    gid = IntegerField(column_name='gid', column_type=MEDIUMINT, primary_key=True)
    count = IntegerField(column_name='count')
    state = StringField(column_name='state', column_type=VARCHAR10)

    def __init__(self, sid, gid, count, state):
        super().__init__()
        self.sid = sid
        self.gid = gid
        self.count = count
        self.state = state


class Purchase(Model):
    __table__ = 'Purchase'

    purchase_id = IntegerField(column_name='purchase_id', column_type=MEDIUMINT, primary_key=True)
    pid = IntegerField(column_name='pid', column_type=MEDIUMINT)
    eid = IntegerField(column_name='eid', column_type=MEDIUMINT)
    checker = IntegerField(column_name='checker')
    wid = IntegerField(column_name='wid', column_type=MEDIUMINT)
    time = TimestampField(column_name='time')

    def __init__(self, pid, eid, checker, wid, time, purchase_id=None):
        super().__init__()
        self.purchase_id = purchase_id
        self.pid = pid
        self.eid = eid
        self.checker = checker
        self.wid = wid
        self.time = time


class PurchaseDetail(Model):
    __table__ = 'PurchaseDetail'

    purchase_id = IntegerField(column_name='purchase_id', column_type=MEDIUMINT, primary_key=True)
    gid = IntegerField(column_name='gid', column_type=MEDIUMINT, primary_key=True)
    price = FloatField(column_name='price')
    state = StringField(column_name='state', column_type=VARCHAR10)

    def __init__(self, purchase_id, gid, price, state):
        super().__init__()
        self.purchase_id = purchase_id
        self.gid = gid
        self.price = price
        self.state = state


class Breakage(Model):
    __table__ = 'Breakage'

    bid = IntegerField(column_name='bid', column_type=MEDIUMINT, primary_key=True)
    eid = IntegerField(column_name='eid', column_type=MEDIUMINT)
    checker = IntegerField(column_name='checker', column_type=MEDIUMINT)
    wid = IntegerField(column_name='wid', column_type=MEDIUMINT)
    time = TimestampField(column_name='time')

    def __init__(self, eid, checker, wid, time, bid=None):
        super().__init__()
        self.bid = bid
        self.eid = eid
        self.checker = checker
        self.wid = wid
        self.time = time


class BreakageDetail(Model):
    __table__ = 'BreakageDetail'

    bid = IntegerField(column_name='bid', column_type=MEDIUMINT, primary_key=True)
    gid = IntegerField(column_name='gid', column_type=MEDIUMINT, primary_key=True)
    count = IntegerField(column_name='count')
    price = FloatField(column_name='price')
    state = StringField(column_name='state', column_type=VARCHAR10)

    def __init__(self, bid, gid, count, price, state):
        super().__init__()
        self.bid = bid
        self.gid = gid
        self.count = count
        self.price = price
        self.state = state














