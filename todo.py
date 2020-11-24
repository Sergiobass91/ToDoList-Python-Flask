from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from toDo.db import get_db
from toDo.auth import required_login

bluePrint = Blueprint('todo',__name__)

@bluePrint.route('/')
@required_login
def index():
    db, c = get_db()
    c.execute(
        'select t.id, t.description, u.username, t.completed, t.created_at from todo t JOIN user u on t.created_by = u.id '
        'where t.created_by = %s order by created_at desc', (g.user['id'],)
    )
    todos = c.fetchall()

    return render_template('todo/index.html', todos=todos)

@bluePrint.route('/create', methods=['GET', 'POST'])
@required_login
def create():
    if request.method == 'POST':
        description = request.form['description']
        error = None
        if not description:
            error = 'Descipcion requerida'
        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute(
                'insert into todo (description, completed, created_by)'
                ' values (%s, %s, %s)', (description, False, g.user['id'])
            )
            db.commit()
            return redirect(url_for('todo.index'))

    return render_template('todo/create.html')

def get_todo(id):
    db,c = get_db()
    c.execute(
        'select t.id, t.description, t.completed, t.created_by, t.created_at, u.username from todo t join user u on t.created_by = u.id where t.id = %s', (id,)
    )
    todo = c.fetchone()

    if todo is None:
        abort(404, f" Task {id} not exists")
    
    return todo

@bluePrint.route('/<int:id>/update', methods=['GET', 'POST'])
@required_login
def update(id):
    todo = get_todo(id)

    if request.method=='POST':
        description = request.form['description']
        completed = True if request.form.get('completed') == 'on' else False
        error = None

        if not description:
            error = 'Description can\'t be empty'
        if error is not None:
            flash(error)
        else:
            db,c = get_db()
            c.execute(
                'update todo set description = %s, completed = %s where id =%s and created_by = %s', (description, completed, id, g.user['id'])
            )
            db.commit()
            return redirect(url_for('todo.index'))

    return render_template('todo/update.html', todo=todo)

@bluePrint.route('/<int:id>/delete', methods=['POST'])
@required_login
def delete(id):
    db,c= get_db()
    c.execute(
        'delete from todo where id = %s and created_by = %s', (id, g.user['id'])
    )
    db.commit()
    return redirect(url_for('todo.index'))
