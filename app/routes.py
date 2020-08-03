from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from . import app, db, login_manager
from .forms import LoginForm, RegistrationForm
from .models import User, Steps

@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        step = Steps.query.filter_by(user_id=current_user.id).first()
        if step is not None:
            if step.get_last_step() is None:
                return render_template('index.html', step=step, username=current_user.username)
            else:
                s1 = step.step1 if step.step1 is not None else ''
                s2 = step.step2 if step.step2 is not None else ''
                s3 = step.step3 if step.step3 is not None else ''
                return render_template('steps.html', uid=current_user.id, step1=s1,
                step2=s2, step3=s3, username=current_user.username)
        else:
            new_step = Steps(user_id=current_user.id)
            db.session.add(new_step)
            db.session.commit()
            return render_template('steps.html', uid=current_user.id, username=current_user.username)
    else:
        return redirect(url_for('login'))

@app.route('/steps/api', methods=['GET'])
def steps():
    if not current_user.is_authenticated:
        return jsonify({'error': 'user is not logged in'})
    if 'id' in request.args:
        id = int(request.args['id'])
        step = Steps.query.filter_by(user_id=id).first()
        if step is not None:
            return jsonify({'last_step_taken': step.get_last_step(),
            'steps': {
                'step1': step.step1,
                'step2': step.step2,
                'step3': step.step3
            }})
    else:
        return jsonify(None)

@app.route('/steps/api/add', methods=['POST'])
def add_step():
    if not current_user.is_authenticated:
        return jsonify({'error': 'user is not logged in'})

    dd = request.get_json()

    if 'id' in dd:
        id = int(dd['id'])
        data = str(dd['data'])

        step = Steps.query.filter_by(user_id=id).first()
        if step is not None:
            last_step = dd['last_step']
            if last_step == 1: step.step1 = data
            elif last_step == 2: step.step2 = data
            elif last_step == 3: step.step3 = data
            db.session.add(step)
            db.session.commit()
            return jsonify({'last_step_taken': step.get_last_step()})
    else:
        return jsonify(None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    next_page = request.args.get('next')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login', next=next_page))

        login_user(user, remember=form.remember_me.data)

        if not next_page:
            return redirect(url_for('index'))
        return redirect(url_for(next_page))

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful')
            return redirect(url_for('login'))
        except:
            flash('Username already taken')
            return render_template('register.html', form=form)

    return render_template('register.html', form=form)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login', next=request.endpoint))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)