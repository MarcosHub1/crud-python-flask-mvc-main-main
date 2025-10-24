import os, uuid
from flask import request, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Pet
from app import app, db
from sqlalchemy import or_
from dotenv import load_dotenv



@app.route('/')
def index():
    termo = request.args.get('q', '')  # pega o termo digitado na busca

    # começa pegando todos os pets
    query = Pet.query

    # se houver termo de pesquisa, filtra por nome ou descrição
    if termo:
        query = query.filter(
            or_(
                Pet.nome.ilike(f"%{termo}%"),
                Pet.descricao.ilike(f"%{termo}%")
            )
        )
    items_ = query.all()
    return render_template('index.html', items=items_)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        # Verifica se já existe usuário com esse email
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Já existe um usuário com esse email.")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(senha, method='sha256')
        new_user = User(nome=nome, email=email, senha=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        flash("Usuário cadastrado com sucesso! Faça login.")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.senha, senha):
            login_user(user)
            return redirect(url_for('perfil'))
        else:
            flash("Email ou senha incorretos.")

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.")
    return redirect(url_for('login'))


from flask import current_app
from app.utils.clip_model import gerar_descricao_clip  # adicione no topo

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

        filename = None
        caminho_imagem = None
        if imagem:
            filename = f"{uuid.uuid4().hex}_{imagem.filename}"
            upload_path = os.path.join(current_app.root_path, "static/uploads", filename)
            imagem.save(upload_path)
            caminho_imagem = upload_path

        # 🧠 Gera descrição automática se houver imagem
        descricao_auto = ""
        if caminho_imagem:
            try:
                descricao_auto = gerar_descricao_clip(caminho_imagem)
            except Exception as e:
                print("Erro ao gerar descrição com CLIP:", e)

        # Junta a descrição escrita pelo usuário com a gerada pela IA
        descricao_final = descricao
        if descricao_auto:
            descricao_final = f"{descricao.strip()} | Descrição automática: {descricao_auto}"

        new_pet = Pet(
            nome=nome,
            tipo=tipo,
            idade=idade,
            descricao=descricao_final,
            status=status,
            contato=contato,
            imagem=filename,
            user_id=current_user.id
        )

        db.session.add(new_pet)
        db.session.commit()
        flash("Pet cadastrado com sucesso! Descrição automática gerada.")

        return redirect(url_for('perfil'))

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
        flash("Pet atualizado com sucesso!")
        return redirect(url_for('index'))

    return render_template('update.html', pet=item)

@app.route('/delete/<int:id>', methods=['GET'])
@login_required
def delete(id):
    item = Pet.query.get_or_404(id)

    if item.user_id != current_user.id:
        flash("Você não tem permissão para excluir este pet.")
        return redirect(url_for('perfil'))

    db.session.delete(item)
    db.session.commit()
    flash("Pet removido com sucesso!")
    return redirect(url_for('perfil'))



@app.route('/perfil')
@login_required
def perfil():
    termo = request.args.get('q', '')  # pega o termo digitado na barra de pesquisa

    # começa buscando apenas os pets do usuário logado
    query = Pet.query.filter_by(user_id=current_user.id)

    # se o usuário digitou algo, filtra por nome OU descrição
    if termo:
        query = query.filter(
            or_(
                Pet.nome.ilike(f"%{termo}%"),
                Pet.descricao.ilike(f"%{termo}%")
            )
        )

    meus_pets = query.all()

    return render_template('perfil.html', items=meus_pets)

