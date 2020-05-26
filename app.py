import os, datetime

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap


app = Flask(__name__, static_folder='assets', template_folder='templates')

Bootstrap(app)

conf_json = os.path.join(os.path.dirname(__file__), 'config.json')

app.config.from_json(conf_json)

db = SQLAlchemy(app)


class Todo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.String(200), nullable=False)
	complete = db.Column(db.Integer, default=0)
	created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
	updated_on = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

	def __repr__(self):
		return '<Task %r>' % self.id


@app.route('/', methods=['GET'])
def index():
	title = 'Todo list'

	todos = Todo.query.order_by(Todo.updated_on.desc()).all()

	return render_template('index.html', todos=todos, title=title)


@app.route('/todo-create', methods=['POST'])
def todo_create():
	content = request.form.get('content')
	if content:
		new_todo = Todo(content=content)
		db.session.add(new_todo)
		db.session.commit()
		flash('Todo added', 'success')
	else:
		flash('Empty field', 'error')	

	return redirect(url_for('index'))


@app.route('/todo-update/<int:id>', methods=['GET', 'POST'])
def todo_update(id):
	todos = Todo.query.order_by(Todo.updated_on.desc()).all()
	todo = Todo.query.get(id)

	if todo:
		if request.method == 'POST':
			content = request.form.get('content')
			
			if not content:
				flash('Empty field', 'error')

				return redirect(url_for('todo_update', id=todo.id))	
			else:
				todo.content = content
				db.session.commit()

				flash('Todo edited', 'success')

				return redirect(url_for('index'))
		else:
			return render_template('index.html', todos=todos, edit_todo=todo)
	else:
		flash('Todo not found', 'error')

		return redirect(url_for('index'))		


@app.route('/todo-delete/<int:id>', methods=['POST'])
def todo_delete(id):
	todo = Todo.query.get_or_404(id)
	db.session.delete(todo)
	db.session.commit()
	flash('Todo deleted', 'success')

	return redirect(url_for('index'))	
	

if __name__=='__main__':
	app.run()