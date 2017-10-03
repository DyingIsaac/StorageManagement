from flask import render_template, flash, redirect, request, url_for
from flask_login import login_required, current_user, logout_user
from ..models import Client, Order, OrderDetail, Good
from ..decorators import client_required
from .forms import ModifyPasswordForm

from . import client


@client.route('/')
@client_required
def index():
    return render_template('client/index.html', nickname=current_user.nickname)


@client.route('/account/', methods=['GET', 'POST'])
@client_required
def account():
    c = Client.query.filter_by('cid={}'.format(current_user.cid)).first()
    if not c:
        flash('账户不存在')
        logout_user()
        return redirect('main.index')

    if request.method == 'POST':
        c.nickname = request.form['nickname']
        if not c.nickname:
            flash('昵称不能为空')
        c.email = request.form['email']
        if not c.email:
            flash('邮箱不能为空')
        c.addr = request.form['addr']
        if not c.addr:
            flash('地址不能为空')
        c.update_db()
        return redirect(url_for('client.account'))
    return render_template('client/account.html', c=c)


@client.route('/modify-pw/', methods=['GET', 'POST'])
@client_required
def modify_password():
    c = Client.query.filter_by('cid={}'.format(current_user.cid)).first()
    if not c:
        flash('账户不存在')
        logout_user()
        return redirect('main.index')

    form = ModifyPasswordForm()
    if form.validate_on_submit():
        c.password = form.password.data
        c.update_db()
        flash('修改成功，请重新登录')
        logout_user()
        return redirect(url_for('auth.login', user_type='client-'))

    return render_template('client/modify-password.html', form=form)


@client.route('/orders/')
@client_required
def orders():
    results = Order.query.filter_by('cid={}'.format(current_user.cid)).all()
    for order in results or ():
        order.details = OrderDetail.query.filter_by('oid={}'.format(order.oid)).all()
        for detail in order.details or ():
            detail.good_name = Good.query.filter_by('gid={}'.format(detail.gid)).first().name
    return render_template('client/orders.html', page_title='我的订单', orders=results)


@client.route('/add-order/', methods=['GET', 'POST'])
@client_required
def add_order():
    if request.method == 'POST':
        gid = request.form.getlist('gid')
        if len(set(gid)) != len(gid):
            flash('货物信息有重复')
            return redirect(url_for('manage.add_purchase'))
        order = Order(current_user.cid, None, '等待发货')
        order.insert_db()
        order = Order.query.all()[-1]
        count = request.form.getlist('count')
        for i in range(len(gid)):
            good = Good.query.filter_by('gid={}'.format(gid[i])).first()
            if not good:
                flash('没有编号为{}的货物的信息'.format(gid[i]))
                return redirect(url_for('manage.add_purchase'))
            OrderDetail(order.oid, good.gid, count[i], good.price).insert_db()
        flash('购货单提交成功!')

    g = Good.query.all()
    return render_template('client/add-order.html', goods=g or [])





