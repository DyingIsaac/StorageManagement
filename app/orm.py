# import logging
import pymysql
from copy import copy
from contextlib import contextmanager


@contextmanager
def connect_db(host='localhost', port=3306, user='root', pw='123456', db='StoreManage', charset='utf8'):
    conn = pymysql.connect(host=host, port=port, user=user, passwd=pw, db=db, charset=charset)
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        yield cursor
    finally:
        conn.commit()
        cursor.close()
        conn.close()


def or_(*args):
    return ' (({})) '.format(') OR ('.join(args))


def and_(*args):
    return ' (({})) '.format((') AND ('.join(args)))


class Query:
    def __init__(self, cls, table, columns, filters=None):
        self.__cls__ = cls
        self.__table__ = table
        self.__columns__ = copy(columns)
        if not filters:
            filters = []
        self.__filters__ = copy(filters)
        self.__statement__ = 'SELECT {} FROM {} '.format(','.join(self.__columns__), self.__table__)
        if self.__filters__:
            self.__statement__ += 'WHERE {} '.format(and_(*self.__filters__))

    def filter_by(self, *filters):
        temp = copy(self.__filters__)
        temp.extend(filters)
        return Query(self.__cls__, self.__table__, self.__columns__, temp)

    def all(self, limit=None):
        with connect_db() as cursor:
            statement = self.__statement__
            if limit:
                if isinstance(limit, int):
                    statement += 'LIMIT %s '
                elif isinstance(limit, tuple):
                    statement += 'LIMIT %s, %s '
                cursor.execute(statement, limit if isinstance(limit, tuple) else (limit,))
            else:
                cursor.execute(statement)
            rows = cursor.fetchall()
            return [self.__cls__(**row) for row in rows] if rows else None

    def first(self):
        with connect_db() as cursor:
            cursor.execute(self.__statement__)
            row = cursor.fetchone()
            return self.__cls__(**row) if row else None


class ModelMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        # 排除Model类自己
        if name == 'Model':
            return type.__new__(mcs, name, bases, attrs)
        # 若设置了__table__属性则使用该属性，否则使用类名作为表名
        table_name = attrs.get('__table__', name)
        # logging.info('found model:{}(table:{})'.format(name, table_name))
        # 获得所有的Field和主键名
        mappings = dict()
        fields = []
        primary_key = []
        for k, v in attrs.items():
            if isinstance(v, Field):
                # logging.info('found mapping: {}==>{}'.format(k, v))
                mappings[k] = v
                if v.primary_key:
                    primary_key.append(k)
                else:
                    fields.append(k)
        if not primary_key:
            raise RuntimeError('Primary key not found.')
        for k in mappings.keys():
            attrs.pop(k)
        # 保存属性和列的映射关系
        attrs['__mappings__'] = mappings
        attrs['__table__'] = table_name
        # 主键属性名
        attrs['__primary_key__'] = primary_key
        # 其他属性名
        attrs['__fields__'] = fields
        attrs['__insert__'] = 'INSERT INTO {} ({}, {}) VALUES ({})'.format(table_name,
                                                                           ','.join(primary_key),
                                                                           ','.join(fields),
                                                                           ','.join('?'*(len(primary_key)+len(fields))))
        attrs['__update__'] = 'UPDATE {} SET {} WHERE {}'.format(table_name,
                                                                 ','.join(['{}=?'.format(f) for f in fields]),
                                                                 ' AND '.join(['{}=?'.format(k) for k in primary_key]))
        attrs['__delete__'] = 'DELETE FROM {} WHERE {}'.format(table_name,
                                                               ' AND '.join(['{}=?'.format(k) for k in primary_key]))
        cls = type.__new__(mcs, name, bases, attrs)
        cls.query = Query(cls, table_name, tuple(mappings.keys()))
        return cls


class Model(metaclass=ModelMetaclass):
    def __init__(self, **kw):
        super().__init__(**kw)

    # def __getattr__(self, key):
    #     try:
    #         return self[key]
    #     except KeyError:
    #         raise AttributeError(r"'Model' object has no attribute '{}'".format(key))
    #
    # def __setattr__(self, key, value):
    #     self[key] = value

    def __str__(self):
        return str({k: getattr(self, k) for k in self.__mappings__.keys()})

    def get_value(self, key):
        return getattr(self, key, None)

    def get_value_or_default(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                # logging.debug('using default value for {}:{}'.format(key, str(value)))
                setattr(self, key, value)
        return value

    def insert_db(self):
        args = [self.get_value_or_default(k) for k in self.__primary_key__]
        args.extend([self.get_value_or_default(k) for k in self.__fields__])
        with connect_db() as cursor:
            rows = cursor.execute(self.__insert__.replace('?', '%s'), args)
            # if rows != 1:
                # logging.warning('failed to insert record: affected rows: {}'.format(rows))

    def update_db(self):
        args = [self.get_value(k) for k in self.__fields__]
        args.extend([self.get_value(k) for k in self.__primary_key__])
        with connect_db() as cursor:
            rows = cursor.execute(self.__update__.replace('?', '%s'), args)
            # if rows != 1:
                # logging.warning('failed to update by primary key: affected rows: {}'.format(rows))

    def remove_db(self):
        args = [self.get_value(k) for k in self.__primary_key__]
        with connect_db() as cursor:
            rows = cursor.execute(self.__delete__, args)
            # if rows != 1:
                # logging.warning('failed to remove by primary key: affected  rows: {}'.format(rows))


class Field:

    def __init__(self, column_name, column_type, primary_key, default):
        self.column_name = column_name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<{},{}>'.format(self.__class__.__name__, self.column_type)


class StringField(Field):

    def __init__(self, column_name, column_type='VARCHAR(100)', primary_key=False, default=None):
        super().__init__(column_name, column_type, primary_key, default)


class IntegerField(Field):

    def __init__(self, column_name, column_type='INT', primary_key=False, default=None):
        super().__init__(column_name, column_type, primary_key, default)


class BooleanFiled(Field):

    def __init__(self, column_name, default=None):
        super().__init__(column_name, 'BOOLEAN', False, default)


class DateField(Field):

    def __init__(self, column_name, primary_key=False, default=None):
        super().__init__(column_name, 'DATE', primary_key, default)


class FloatField(Field):

    def __init__(self, column_name, primary_key=False, default=None):
        super().__init__(column_name, 'FLOAT', primary_key, default)


class TextField(Field):

    def __init__(self, column_name, column_type='TEXT', primary_key=False, default=None):
        super().__init__(column_name, column_type, primary_key, default)


class PasswordField(Field):

    def __init__(self, column_name, primary_key=False):
        super().__init__(column_name, 'CHAR(128)', primary_key, None)


class TimestampField(Field):

    def __init__(self, column_name, primary_key=False):
        super().__init__(column_name, 'TIMESTAMP', primary_key, None)
