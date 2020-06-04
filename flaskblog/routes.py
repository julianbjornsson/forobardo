import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import LoginForm, RegistrationForm, UpdateAccountForm, PostForm, CommentForm, AdminForm, RequestResetForm, ResetPasswordForm
from flaskblog.models import User, Post, Comment
from flask_login import login_user, current_user, logout_user, login_required
from datetime import time, datetime, date
from pytz import timezone
from flask_mail import Message

"""
posts = [
    {
        'author': 'Julian',
        'title': 'El paradigma monotesticular',
        'content': 'Hay algunos seres que presentan una rara condicion que los fuerza a ejercer solo la mitad de su capacidad seminal a lo largo de su vida, el "monotesticulismo". Este es el caso de uno de los pocos conocidos que sufren esta afliccion, Cuenca, Leonel, mas conocido como "Elgo"',
        'date_created': '20 de Abril del 2020'
    },
    {
        'author': 'Juan Carlos',
        'title': 'El paradigma gigantopeneano',
        'content': 'Tambien, en los anales de la historia, se han registrado seres con una capacidad unica para redirigir la masa de su cuerpo a sectores poco convencionales. Este es el caso de "Franco Donato", el hombre que logro manipular cada atomo de su cuerpo y redirigir gran parte de su masa hacia su zona pelvica, mas especificamente hacia su virilidad. Este individuo presenta un tamaño desmedido y poco humano en donde deberia estar su otrora pene, quien (quien porque es una entidad viva y consciente de si misma, mas inteligente que su portadort) logro tomar total dominio de su "portador", mas conocido como "Elver"',
        'date_created': '20 de Mayo del 2020'
    }
]
"""
@app.route('/')
def entrada():
    return render_template('initial.html', title='Bienvenido')

@app.route('/home')
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
    autor = current_user
    return render_template('home.html', posts=posts, autor=autor)
    

@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'La cuenta fue creada con exito, ya puedes iniciar sesion', 'success') 
        return redirect(url_for('login'))
    return render_template('register.html', title='Registro', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
        else:
            flash('El correo electronico o la contraseña ingresados son invalidos. Por favor, intente nuevamente', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('Has cerrado sesion', 'info')
    return render_template('initial.html')

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    output_size = (300,125)
    i = Image.open(form_picture)
    i.save(picture_path)

    return picture_fn

@app.route('/cuenta', methods=['GET', 'POST'])
@login_required
def cuenta():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Su cuenta ha sido actualizada', 'success')
        return redirect(url_for('cuenta'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    posts = Post.query.filter_by(author=current_user).order_by(Post.date_posted.desc()).all()
    image_file = url_for('static', filename='/profile_pics/' + current_user.image_file)
    return render_template('cuenta.html', title='Mi Cuenta', image_file=image_file, form=form, posts=posts)

def subir_foto(form_img):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_img.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/post_pics', picture_fn)

    output_size = (125,125)
    i = Image.open(form_img)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        if form.img.data:
            picture_file = subir_foto(form.img.data)
            post = Post(title=form.title.data, content=form.content.data, author=current_user, image=picture_file)
            post.image = picture_file
            db.session.add(post)
            db.session.commit()
            flash('Posteado con exito', 'success')
            return redirect(url_for('home'))
        else:
            post = Post(title=form.title.data, content=form.content.data, author=current_user)
            db.session.add(post)
            db.session.commit()
            flash('Posteado con exito', 'success')
            return redirect(url_for('home'))
    return render_template('create_post.html', title='Nuevo Post', form=form, legend='Nuevo Post')

@app.route('/post/<int:post_id>')
def post(post_id):

    post = Post.query.get_or_404(post_id)
    com = Comment.query.filter_by(post_id=post.id).order_by(Comment.date_posted.desc()).all()
    return render_template('post.html', title=post.title, post=post, com=com)

@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('El post se actualizo correctamente', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Actualizar', form=form, legend='Modificar Post')

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('El post ha sido eliminado', 'success')
    return redirect(url_for('home'))

@app.route('/user/<string:username>')
def user_posts(username):
        page = request.args.get('page', 1, type=int)
        user = User.query.filter_by(username=username).first_or_404()
        nombre = User.query.get(username)
        image = User.query.filter_by(username=username).first()
        posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
        return render_template('user_post.html', posts=posts, user=user, image=image, nombre=nombre)

@app.route('/update_account', methods=['GET', 'POST'])
@login_required
def update_account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.about = form.about.data
        db.session.commit()
        flash('Su cuenta ha sido actualizada', 'success')
        return redirect(url_for('cuenta'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about.data = current_user.about
    posts = Post.query.filter_by(author=current_user).order_by(Post.date_posted.desc()).all()
    image_file = url_for('static', filename='/profile_pics/' + current_user.image_file)
    return render_template('update_account.html', title='Modificar cuenta', image_file=image_file, form=form, posts=posts)

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {{ username }} not found.', 'success')
        return redirect(url_for('home'))
    if user == current_user:
        flash('You cannot follow yourself!', 'info')
        return redirect(url_for('user_posts', username=username))
    current_user.follow(user)
    db.session.commit()
    flash("Ahora seguis a {}".format(user.username), 'success')
    return redirect(url_for('user_posts', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {{ user.username }} not found.', 'success')
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!','info')
        return redirect(url_for('user_posts', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('Ya no estas linkeado a @{}'.format(user.username), 'success')
    return redirect(url_for('user_posts', username=username))  

@app.route('/admin', methods=['GET', 'POST'])  
@login_required
def admin_user():
    form = AdminForm()
    if current_user.id == 2:
        return redirect(url_for('admin.index'))
    else:
        flash("Usuario no autorizado", 'danger')
        return redirect(url_for('home'))


@app.route("/post/<int:post_id>/comment", methods=["GET", "POST"])
@login_required
def comment_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    user = current_user
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, post_id=post.id, user_id=current_user.username, image=user.image_file)
        db.session.add(comment)
        db.session.commit()
        flash("Comentario añadido", "success")
        return redirect(url_for("post", post_id=post.id))
    return render_template("comment_post.html", title="Opina", form=form)

@app.route('/chat_grupal')
@login_required
def chat_grupal():
    return render_template("chatg.html")

def send_reset_email(user):
    token = user.get_reset_token()    
    msg = Message('Solicitud de cambio de contraseña', sender='noreply@forobardo.com', recipients=[user.email])
    msg.body = f'''Para reiniciar tu clave, ve a 
{url_for('reset_token', token=token, _external=True)}
Si no solicitaste el cambio, ignora este mensaje
    '''
    mail.send(msg)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Se ha enviado un correo con instrucciones para reiniciar su clave', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reiniciar contraseña', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Token invalido o expirado', 'danger')
        return redirect(url_for('reset_request'))  
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'La clave fue reiniciada', 'success') 
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reiniciar contraseña', form=form)     
