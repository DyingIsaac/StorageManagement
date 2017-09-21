from flask import render_template, request, flash, redirect, url_for, abort
from ..decorators import employee_required
from .forms import AddEmployeeForm, AddWarehouseForm
from datetime import date
from ..models import Employee, Client, Warehouse, Order, OrderDetail, Good
from ..orm import and_, or_

from . import manage


def _check_id(idname, query, filters):
    myid = request.args.get(idname, None)
    if myid:
        try:
            myid = int(myid)
            query.append('{}={}'.format(idname, myid))
            filters[idname] = myid
        except ValueError:
            flash('编号必须为数字')


def _datefstr(timestr):
    if timestr and len(timestr)==10 :
        try:
            year = int(timestr[:4])
            month = int(timestr[5:7])
            day = int(timestr[8:])
            year, month, day = map(int, timestr.split('-'))
        except ValueError:
            flash('日期中只能含有数字')
            return None
        try:
            d = date(year, month, day)
        except ValueError:
            flash('日期不合法')
            return None
        if d > date.today():
            flash('日期大于今天')
            return None
        return d
    return None






@manage.route('/employees/<nickname>/')
@employee_required
def index(nickname):
    return render_template("management/index.html", page_title='管理', nickname=nickname)


@manage.route('/add-employee/', methods=['GET', 'POST'])
@employee_required
def add_employee():
    form = AddEmployeeForm()
    if form.validate_on_submit():
        employee = Employee(form.name.data, form.sex.data, form.email.data,
                            form.name.data, None, '无', form.birthday.data)
        employee.password = form.password.data
        employee.insert_db()
        flash('添加成功')
        return redirect(url_for('manage.add_employee'))
    return render_template('management/add-employee.html', page_title='添加员工', form=form)


@manage.route('/employees/')
@employee_required
def employees():
    query = []
    filters = dict()
    _check_id('eid', query, filters)
    name = request.args.get('name', None)
    if name:
        query.append('name="{}"'.format(name))
        filters['name'] = name
    sex = request.args.get('sex', None)
    if sex:
        query.append('sex="{}"'.format(sex))
        filters['sex'] = sex
    email = request.args.get('email', None)
    if email:
        query.append('email="{}"'.format(email))
        filters['email'] = email
    addr = request.args.get('addr', None)
    if addr:
        query.append('addr="{}"'.format(addr))
        filters['addr'] = addr
    age = request.args.get('age', None)
    birthday = request.args.get('birthday', None)
    if age and birthday:
        flash('不能同时检索生日和年龄')
    elif age:
        try:
            birthday = date.today()
            birthday = birthday.replace(year=birthday.year-int(age))
            f = '(birthday < "{}" AND '.format(birthday.strftime('%Y-%m-%d'))
            f += 'birthday >= "{}")'
            birthday = birthday.replace(year=birthday.year-1)
            query.append(f.format(birthday.strftime('%Y-%m-%d')))
            filters['age'] = age
        except ValueError:
            flash('年龄必须为数字')
    elif birthday:
        query.append('birthday="{}"'.format(birthday))
        filters['birthday'] = birthday

    q = Employee.query
    if len(query) > 0:
        q = q.filter_by(*query)
    return render_template('management/employees.html', page_title='员工信息', employees=q.all(), filters=filters)


@manage.route('/clients/')
@employee_required
def clients():
    query = []
    filters = dict()
    _check_id('cid', query, filters)
    name = request.args.get('name', None)
    if name:
        query.append('name="{}"'.format(name))
        filters['name'] = name
    email = request.args.get('email', None)
    if email:
        query.append('email="{}"'.format(email))
        filters['email'] = email
    addr = request.args.get('addr', None)
    if addr:
        query.append('addr="{}"'.format(addr))
        filters['addr'] = addr

    q = Client.query
    if len(query) > 0:
        q = q.filter_by(*query)
    return render_template('management/clients.html', page_title='客户信息', clients=q.all(), filters=filters)


@manage.route('/warehouses/')
@employee_required
def warehouses():
    query = []
    filters = dict()
    _check_id('wid', query, filters)
    name = request.args.get('name', None)
    if name:
        query.append('name="{}"'.format(name))
        filters['name'] = name
    addr = request.args.get('addr', None)
    if addr:
        query.append('addr="{}"'.format(addr))
        filters['addr'] = addr

    q = Warehouse.query
    if len(query) > 0:
        q = q.filter_by(*query)
    return render_template('management/warehouses.html', page_title='仓库信息', warehouses=q.all(), filters=filters)


@manage.route('/add-warehouse/', methods=['GET', 'POST'])
@employee_required
def add_warehouse():
    form = AddWarehouseForm()
    if form.validate_on_submit():
        Warehouse(form.name.data, form.addr.data).insert_db()
        flash('添加成功')
        return redirect(url_for('manage.add_employee'))
    return render_template('management/add-warehouse.html', page_title='添加仓库', form=form)


@manage.route('/orders/')
@employee_required
def orders():
    query = []
    filters = dict()
    _check_id('oid', query, filters)
    _check_id('cid', query, filters)
    min_date = _datefstr(request.args.get('min_date'))
    if min_date:
        query.append('time>={}'.format(min_date))
        filters['min_date'] = min_date
    max_date = _datefstr(request.args.get('max_date'))
    if max_date:
        query.append('time<={}'.format(max_date))
        filters['max_date'] = max_date
    state = request.args.get('state')
    if state:
        query.append('state={}'.format(state))
        filters['state'] = state
    q = Order.query
    if len(query) > 0:
        q = q.filter_by(*query)
    results = q.all()
    if results:
        for order in results:
            order.details = OrderDetail.query.filter_by('oid={}'.format(order.oid), 'cid={}'.format(order.cid)).all()
            for detail in order.details:
                detail.good_name = Good.query.filter_by('gid={}'.format(detail.gid))
    return render_template('management/orders.html', page_title='订单信息', orders=results, filters=filters)





















