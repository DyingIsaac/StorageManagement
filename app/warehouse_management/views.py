from flask import render_template, request, flash, redirect, url_for, abort, make_response
from flask_login import current_user, logout_user
from ..decorators import employee_required, su_required
from .forms import AddEmployeeForm, AddWarehouseForm, ModifyPasswordForm, AddProviderForm, AddGoodForm, AddTypeForm
from datetime import date
from ..models import Employee, Client, Warehouse, Order, OrderDetail, Good, Purchase, PurchaseDetail, Provider,\
    Provide, StockIn, StockOut, Store, Type
from ..orm import and_, or_

from . import manage


def _check_id(idname, query, filters):
    myid = request.args.get(idname, None)
    if myid:
        myid = int(myid)
        query.append('{}={}'.format(idname, myid))
        filters[idname] = myid


def _datefstr(timestr):
    if timestr and len(timestr) == 10:
        try:
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


@manage.route('/providers/')
@employee_required
def providers():
    query = []
    filters = dict()
    _check_id('pid', query, filters)
    name = request.args.get('name', None)
    if name:
        query.append('name="{}"'.format(name))
        filters['name'] = name
    addr = request.args.get('addr', None)
    if addr:
        query.append('addr="{}"'.format(addr))
        filters['addr'] = addr

    q = Provider.query
    if len(query) > 0:
        q = q.filter_by(*query)
    return render_template('management/providers.html', page_title='供应商信息', providers=q.all(), filters=filters)


@manage.route('/providers/<int:pid>/')
@employee_required
def provider(pid):
    p = Provider.query.filter_by('pid={}'.format(pid)).first()
    if not p:
        abort(404)
    provides = Provide.query.filter_by('pid={}'.format(pid)).all()
    goods = []
    for provide in provides or []:
        g = Good.query.filter_by('gid={}'.format(provide.gid)).first()
        g.price = provide.price
        goods.append(g)
    return render_template('management/provider.html', page_title='供应商详情', provider=p, goods=goods)


@manage.route('/add-provider/', methods=['GET', 'POST'])
@su_required
def add_provider():
    form = AddProviderForm()
    if form.validate_on_submit():
        Provider(form.name.data, form.addr.data).insert_db()
        flash('添加成功')
        return redirect((url_for('manage.add_provider')))
    return render_template('management/add-provider.html', page_title='添加供应商', form=form)


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


@manage.route('/warehouses/<int:wid>/')
@employee_required
def warehouse(wid):
    w = Warehouse.query.filter_by('wid={}'.format(wid)).first()
    if not w:
        abort(404)
    stores = Store.query.filter_by('wid={}'.format(wid)).all()
    for store in stores or []:
        store.good = Good.query.filter_by('gid={}'.format(store.gid)).first()
    return render_template('management/warehouse.html', page_title='仓库详情', warehouse=w, stores=stores)


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
    min_date = _datefstr(request.args.get('min_date', None))
    if min_date:
        query.append('time>={}'.format(min_date))
        filters['min_date'] = min_date
    max_date = _datefstr(request.args.get('max_date', None))
    if max_date:
        query.append('time<={}'.format(max_date))
        filters['max_date'] = max_date
    state = request.args.get('state')
    if state:
        query.append('state="{}"'.format(state))
        filters['state'] = state
    q = Order.query
    if len(query) > 0:
        q = q.filter_by(*query)
    results = q.all()
    if results:
        for order in results:
            order.details = OrderDetail.query.filter_by('oid={}'.format(order.oid), 'cid={}'.format(order.cid)).all()
            for detail in (order.details or []):
                detail.good_name = Good.query.filter_by('gid={}'.format(detail.gid))
    return render_template('management/orders.html', page_title='订单信息', orders=results or [], filters=filters or [])


@manage.route('/goods/')
@employee_required
def goods():
    query = []
    filters = dict()
    _check_id('gid', query, filters)
    _check_id('tid', query, filters)
    name = request.args.get('name', None)
    if name:
        query.append('name={}'.format(name))
        filters['name'] = name
    q = Good.query
    if len(query) > 0:
        q = q.filter_by(*query)
    return render_template('management/goods.html', page_title='货物信息', goods=q.all(), filters=filters or [])


@manage.route('/add-good/')
@employee_required
def add_good():
    form = AddGoodForm()
    if form.validate_on_submit():
        Good(form.name.data, form.tid.data, form.price.data).insert_db()
        flash('添加成功！')
        return redirect(url_for('manage.add_good'))
    return render_template('management/add-good.html', page_title='添加货物', form=form)


@manage.route('/types/')
@employee_required
def types():
    query = []
    filters = dict()
    _check_id('tid', query, filters)
    name = request.args.get('name', None)
    if name:
        query.append('name={}'.format(name))
        filters['name'] = name
    q = Type.query
    if len(query) > 0:
        q = q.filter_by(*query)
    return render_template('management/types.html', page_title='类别信息', types=q.all(), filters=filters)


@manage.route('/add-type/')
@employee_required
def add_type():
    form = AddTypeForm()
    if form.validate_on_submit():
        Type(form.name.data, form.parent.data).insert_db()
        flash('添加成功！')
        return redirect(url_for('manage.add_type'))
    return render_template('management/add-type.html', page_title='添加类别', form=form)


@manage.route('/purchases/')
@employee_required
def purchases():
    query = []
    filters = dict()
    _check_id('purchase_id', query, filters)
    _check_id('pid', query, filters)
    _check_id('eid', query, filters)
    _check_id('checker', query, filters)
    _check_id('wid', query, filters)
    state = request.args.get('state')
    if state:
        query.append('state="{}"'.format(state))
        filters['state'] = state
    q = Purchase.query
    if len(query)>0:
        q = q.filter_by(*query)
    results = q.all()
    if results:
        for purchase in results:
            purchase.details = PurchaseDetail.query.filter_by('purchase_id={}'.format(purchase.purchase_id)).all() or []
            for detail in (purchase.details or []):
                detail.good_name = Good.query.filter_by('gid={}'.format(detail.gid)).first().name
    return render_template('management/purchases.html', page_title='购货单信息', purchases=results or [], filters=filters or [])


@manage.route('/add-stock-in/', methods=['GET', 'POST'])
@employee_required
def add_stock_in():
    if request.method == 'POST':
        wid = request.form['wid']
        gid = request.form.get('gid')
        count = int(float(request.form.get('count')))
        reason = request.form.get('reason')
        extra = request.form.get('extra')

        if reason == '采购':
            pd = PurchaseDetail.query.filter_by('purchase_id={}'.format(extra), 'gid={}'.format(gid)).first()
            if not pd:
                flash('没有采购信息！')
            elif pd.state == '已入库':
                flash('已入库！')
            elif pd.count != count:
                flash('商品数量不匹配！')
            else:
                pd.state = '已入库'
                pd.update_db()
                StockIn(wid, gid, current_user.eid, count, None, reason, extra).insert_db()
                flash('购货单提交成功!')
                return redirect(url_for('manage.add_stock_in'))
        else:
            StockIn(wid, gid, current_user.eid, count, None, reason, extra).insert_db()
            flash('购货单提交成功!')
            return redirect(url_for('manage.add_stock_in'))


    w = Warehouse.query.all()
    g = Good.query.all()
    return render_template('management/add-stock-in.html', warehouses=w or [], goods=g or [])


@manage.route('/stock-ins/')
@employee_required
def stock_ins():
    query = []
    filters = dict()
    _check_id('siid', query, filters)
    _check_id('wid', query, filters)
    _check_id('gid', query, filters)
    _check_id('eid', query, filters)

    reason = request.args.get('reason')
    if reason:
        query.append('reason="{}"'.format(reason))
        filters['reason'] = reason

    extra = request.args.get('extra')
    if extra:
        query.append('extra={}'.format(extra))
        filters['extra'] = extra

    q = StockIn.query
    if len(query) > 0:
        q = q.filter_by(*query)
    results = q.all()
    return render_template('management/stock-ins.html', page_title='入库单', stock_ins=results or [], filters=filters or [])


@manage.route('/add-stock-out/', methods=['GET', 'POST'])
@employee_required
def add_stock_out():
    if request.method == 'POST':
        wid = request.form.get('wid')
        gid = request.form.get('gid')
        count = int(float(request.form.get('count')))
        reason = request.form.get('reason')
        extra = request.form.get('extra')

        if reason == '用户订单':
            od = OrderDetail.query.filter_by('oid={}'.format(extra), 'gid={}'.format(gid)).first()
            if not od:
                flash('没有订单信息！')
            elif od.state == '已出库':
                flash('已出库！')
            elif od.count != count:
                flash('商品数量不匹配！')
            else:
                od.state = '已出库'
                od.update_db()
                StockOut(wid, gid, current_user.eid, count, None, reason, extra).insert_db()
                flash('购货单提交成功!')
                return redirect(url_for('manage.add_stock_out'))
        else:
            StockOut(wid, gid, current_user.eid, count, None, reason, extra).insert_db()
            flash('购货单提交成功!')
            return redirect(url_for('manage.add_stock_out'))

    w = Warehouse.query.all()
    g = Good.query.all()
    return render_template('management/add-stock-out.html', warehouses=w or [], goods=g or [])


@manage.route('/stock-outs/')
@employee_required
def stock_outs():
    query = []
    filters = dict()
    _check_id('soid', query, filters)
    _check_id('wid', query, filters)
    _check_id('gid', query, filters)
    _check_id('eid', query, filters)

    reason = request.args.get('reason')
    if reason:
        query.append('reason="{}"'.format(reason))
        filters['reason'] = reason

    extra = request.args.get('extra')
    if extra:
        query.append('extra={}'.format(extra))
        filters['extra'] = extra

    q = StockOut.query
    if len(query) > 0:
        q = q.filter_by(*query)
    results = q.all()
    return render_template('management/stock-outs.html', page_title='入库单', stock_outs=results, filters=filters or [])


@manage.route('/add-purchase/', methods=['GET', 'POST'])
@employee_required
def add_purchase():
    if request.method == 'POST':
        pid = request.form['pid']
        if not Provider.query.filter_by('pid={}'.format(pid)).first():
            flash('没有编号为{}的供应商'.format(pid))
            return redirect(url_for('manage.add_purchase'))

        wid = request.form['wid']
        if not Warehouse.query.filter_by('wid={}'.format(wid)).first():
            flash('没有编号为{}的仓库'.format(wid))
            return redirect(url_for('manage.add_purchase'))

        gid = request.form.getlist('gid')
        if len(set(gid)) != len(gid):
            flash('货物信息有重复')
            return redirect(url_for('manage.add_purchase'))
        purchase = Purchase(pid, current_user.eid, None, wid, None)
        purchase.insert_db()
        purchase = Purchase.query.all()[-1]
        count = request.form.getlist('count')
        for i in range(len(gid)):
            provide = Provide.query.filter_by('pid={}'.format(pid), 'gid={}'.format(gid[i])).first()
            if not provide:
                flash('该供应商不提供编号为{}的货物'.format(gid[i]))
                return redirect(url_for('manage.add_purchase'))
            PurchaseDetail(purchase.purchase_id, gid[i], provide.price, count[i], '未到货').insert_db()
        flash('购货单提交成功!')

    p = Provider.query.all()
    w = Warehouse.query.all()
    g = Good.query.all()
    return render_template('management/add-purchase.html', providers=p or [], warehouses=w or [], goods=g or [])


@manage.route('/check_purchases/<purchase_id>/', methods=['GET', 'POST'])
@employee_required
def check_purchase_detail(purchase_id):
    p = Purchase.query.filter_by('purchase_id={}'.format(purchase_id)).first()
    if p and p.state == '未审核':
        p.state = '已审核'
        p.checker = current_user.eid
        p.update_db()
        return ('OK', 200)
    return ('购货单不存在或已审核，请刷新后重试', 404)


@manage.route('/account/', methods=['GET', 'POST'])
@employee_required
def account():
    e = Employee.query.filter_by('eid={}'.format(current_user.eid)).first()
    if not e:
        flash('账户不存在')
        logout_user()
        return redirect('main.index')

    if request.method == 'POST':
        e.nickname = request.form['nickname']
        if not e.nickname:
            flash('昵称不能为空')
        e.email = request.form['email']
        if not e.email:
            flash('邮箱不能为空')
        e.addr = request.form['addr']
        if not e.addr:
            flash('地址不能为空')
        e.update_db()
        return redirect(url_for('manage.account'))
    return render_template('management/account.html', e=e)


@manage.route('/modify-pw/', methods=['GET', 'POST'])
@employee_required
def modify_password():
    e = Employee.query.filter_by('eid={}'.format(current_user.eid)).first()
    if not e:
        flash('账户不存在')
        logout_user()
        return redirect('main.index')

    form = ModifyPasswordForm()
    if form.validate_on_submit():
        e.password = form.password.data
        e.update_db()
        flash('修改成功，请重新登录')
        logout_user()
        return redirect(url_for('auth.login'))

    return render_template('management/modify-password.html', form=form)










