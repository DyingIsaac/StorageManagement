from flask import render_template, request, flash, redirect, url_for
from ..decorators import employee_reauired
from .forms import AddEmployeeForm, AddWarehouseForm
from datetime import date
from ..models import Employee, Client, Warehouse
from ..orm import and_, or_

from . import manage


@manage.route('/employees/<nickname>/')
@employee_reauired
def index(nickname):
    return render_template("management/index.html", page_title='管理', nickname=nickname)


@manage.route('/add-employee/', methods=['GET', 'POST'])
@employee_reauired
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
@employee_reauired
def employees():
    query = []
    filters = dict()
    eid = request.args.get('eid', None)
    if eid:
        try:
            eid = int(eid)
            query.append('eid={}'.format(int(eid)))
            filters['eid'] = eid
        except ValueError:
            flash('编号必须为数字')
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
@employee_reauired
def clients():
    query = []
    filters = dict()
    cid = request.args.get('cid', None)
    if cid:
        try:
            cid = int(cid)
            query.append('cid={}'.format(int(cid)))
            filters['cid'] = cid
        except ValueError:
            flash('编号必须为数字')
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
@employee_reauired
def warehouses():
    query = []
    filters = dict()
    wid = request.args.get('wid', None)
    if wid:
        try:
            wid = int(wid)
            query.append('wid={}'.format(int(wid)))
            filters['wid'] = wid
        except ValueError:
            flash('编号必须为数字')
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
@employee_reauired
def add_warehouse():
    form = AddWarehouseForm()
    if form.validate_on_submit():
        Warehouse(form.name.data, form.addr.data).insert_db()
        flash('添加成功')
        return redirect(url_for('manage.add_employee'))
    return render_template('management/add-warehouse.html', page_title='添加仓库', form=form)






















