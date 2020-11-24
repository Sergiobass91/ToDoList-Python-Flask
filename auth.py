import functools
from  flask import(
    Blueprint, flash, g, render_template, request, url_for, session, redirect
)
from werkzeug.security import check_password_hash, generate_password_hash
from toDo.db import get_db

bluePrint =  Blueprint('auth',__name__,url_prefix='/auth') #identificador de usuario


@bluePrint.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db,c = get_db()
        error = None
        c.execute('select id from user where username = %s', (username,))

        if not username:
            error = 'Username is required'
        if not password:
            error = 'Password is required'
        elif c.fetchone() is not None:
            error = 'User {} is registered'.format(username)

        if error is None:
            c.execute(
                'insert into user (username, password) values (%s, %s)',
                (username, generate_password_hash(password))
            )
            db.commit()
        
            return redirect(url_for('auth.login'))
    
        flash(error)

    return render_template('auth/register.html')

@bluePrint.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db, c = get_db()
        error =None
        c.execute(
            'select * from user where username = %s', (username,)
        )
        user = c.fetchone()
        if user is None:
            error = 'Usuario y/o Contraseña invalida'
        elif not check_password_hash(user['password'], password):
            error = 'Usuario y/o Contraseña invalida'
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            
            return redirect(url_for('todo.index'))

        flash(error)

    return render_template('auth/login.html')

@bluePrint.before_app_request
def load_logged_in_user():
    user_id= session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db, c = get_db()
        c.execute(
            'select * from user where id = %s', (user_id,)
        )
        g.user = c.fetchone() #Retorna el primer elemento que encuentra (list of dict)

def required_login(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view

@bluePrint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))