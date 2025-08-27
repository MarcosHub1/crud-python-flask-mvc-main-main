from flask import request, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from app.models import User, Pet

@app.route('/')
def index():
    items_ = Pet.query.all()
    return render_template('index.html', items=items_)

# Cadastro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        # Verifica se já existe um usuário com esse email
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email já cadastrado!')
            return redirect(url_for('register'))

        new_user = User(nome=nome, email=email)
        new_user.set_password(senha)

        db.session.add(new_user)
        db.session.commit()

        flash('Cadastro realizado com sucesso! Faça login.')
        return redirect(url_for('login'))

    return render_template('register.html')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(senha):
            login_user(user)
            flash('Login realizado com sucesso!')
            return redirect(url_for('index'))
        else:
            flash('Email ou senha incorretos.')

    return render_template('login.html')


# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.')
    return redirect(url_for('login'))

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        nome = request.form['nome']
        tipo = request.form['tipo']
        idade = request.form['idade']
        descricao = request.form['descricao']
        status = request.form['status']
        contato = request.form['contato']
        imagem = request.files['imagem'] if 'imagem' in request.files else None

        new_pet = Pet(
            nome=nome,
            tipo=tipo,
            idade=idade,
            descricao=descricao,
            status=status,
            contato=contato,
            imagem=imagem.filename if imagem else None,  # por enquanto só salva o nome do arquivo
            user_id=current_user.id
            )

        if imagem:
            imagem.save(f"app/static/uploads/{imagem.filename}")  # salva a imagem no servidor

        db.session.add(new_pet)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('create.html')


@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    item = Pet.query.get_or_404(id)
    if item.user_id != current_user.id:
        flash("Você não tem permissão para editar este pet.")
        return redirect(url_for('index'))
    if request.method == 'POST':
        item.nome = request.form['nome']
        item.tipo = request.form['tipo']
        item.idade = request.form['idade']
        item.descricao = request.form['descricao']
        item.status = request.form['status']
        item.contato = request.form['contato']

        imagem = request.files['imagem'] if 'imagem' in request.files else None
        if imagem and imagem.filename != '':
            imagem.save(f"app/static/uploads/{imagem.filename}")
            item.imagem = imagem.filename

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('update.html', item=item)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    item = Pet.query.get_or_404(id)
    if item.user_id != current_user.id:
        flash("Você não tem permissão para deletar este pet.")
        return redirect(url_for('index'))
    db.session.delete(item)
    db.session.commit()
    flash("Pet deletado com sucesso!")
    return redirect(url_for('index'))

@app.route('/perfil')
@login_required
def perfil():
    meus_pets = Pet.query.filter_by(user_id=current_user.id).all()
    return render_template('perfil.html', items=meus_pets)