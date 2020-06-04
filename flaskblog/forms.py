from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=6, max=15)])

    email = StringField('Correo electronico', validators=[DataRequired(), Email()])
    
    password = PasswordField('Contraseña', validators=[DataRequired()])

    confirm_password = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('password')])
    
    submit = SubmitField('Registrarse')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('El usuario esta en uso, elije otro')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('El correo electronico ya esta registrado')

class LoginForm(FlaskForm):
    email = StringField('Correo electronico', validators=[DataRequired(), Email()])
    
    password = PasswordField('Contraseña', validators=[DataRequired()])

    remember = BooleanField('Recordarme')
    
    submit = SubmitField('Ingresar')

class UpdateAccountForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=6, max=15)])

    email = StringField('Correo electronico', validators=[DataRequired(), Email()])

    picture = FileField('Cambiar foto', validators=[FileAllowed(['jpg', 'png'])])

    about = StringField('Acerca de mi', validators=[Length(min=40, max=400), DataRequired()])
    
    submit = SubmitField('Modificar Datos')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('El usuario esta en uso, elije otro')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('El correo electronico ya esta registrado')

class PostForm(FlaskForm):
    title = StringField('Titulo', validators=[DataRequired()])
    content = TextAreaField('Contenidos', validators=[DataRequired()])
    img = FileField('Subir foto', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Postear')

class CommentForm(FlaskForm):
    content = TextAreaField('Tu opinion:', validators=[DataRequired()])
    submit = SubmitField('Comentar')

class AdminForm(FlaskForm):
    email = StringField('Correo electronico', validators=[DataRequired(), Email()])
    
    password = PasswordField('Contraseña', validators=[DataRequired()])
    
    submit = SubmitField('Ingresar')

class RequestResetForm(FlaskForm):
    email = StringField('Correo electronico', validators=[DataRequired(), Email()])
    submit = SubmitField('Solicitar cambio de contraseña')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('No hay cuentas con esos datos. Debes registrarte primero')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Contraseña', validators=[DataRequired()])

    confirm_password = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Reestablecer contraseña')