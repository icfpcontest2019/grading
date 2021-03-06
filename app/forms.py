from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, TextAreaField, TextField
from wtforms.validators import DataRequired, Email, ValidationError
from flask_wtf.file import FileField, FileRequired, FileAllowed
import tempfile, zipfile
from werkzeug.utils import secure_filename
from app import db, contest
from app.models import Team

# Registration
def name_unique(form, field):
    name = field.data
    q = db.session.query(Team).filter(Team.name == name)
    already_exists = db.session.query(q.exists()).scalar()
    if already_exists:
        raise ValidationError('Name {} is already taken! Choose another.'.format(name))

def email_unique(form, field):
    email = field.data
    q = db.session.query(Team).filter(Team.email == email)
    already_exists = db.session.query(q.exists()).scalar()
    if already_exists:
        raise ValidationError('Email {} has already been used. If you think this is an error, contact the organisers.'.format(email))

def no_redundant_spaces(form, field):
    if field.data != field.data.strip():
        raise ValidationError('Please remove leading/trailing whitespace.')

class RegisterForm(FlaskForm):
    team_name = StringField('Team name', validators=[DataRequired(message=u'You must enter a team name.'), name_unique, no_redundant_spaces])
    email = StringField('Email', validators=[Email(message=u'That\'s not a valid email address.'), email_unique])
    submit = SubmitField('Register')

# Profile
def priv_id_exists(form, field):
    priv_id = field.data
    q = db.session.query(Team).filter(Team.private_id == priv_id)
    already_exists = db.session.query(q.exists()).scalar()
    if not already_exists:
        raise ValidationError('Private ID not found. Have you mistyped it?')

class PrivForm(FlaskForm):
    private_id = StringField('What is your private ID?', validators=[priv_id_exists])
    submit = SubmitField('Login')

class ProfileForm(FlaskForm):
    team_name = StringField('Team name', validators=[DataRequired(message=u'You must enter a team name.'), no_redundant_spaces])
    email = StringField('Email', validators=[Email(message=u'That\'s not a valid email address.')])
    members = TextAreaField('Team members')
    countries = TextField('Countries')
    langs = TextField('Programming languages')
    file = FileField('Source code ZIP', validators=[FileAllowed(['zip'], 'Please upload a file with .zip extension.')])
    comments = TextAreaField('Comments')
    submit = SubmitField('Update profile')

# Submission

def top_level_dirs(namelist):
    with_tld = [x for x in namelist if '/' in x]
    return with_tld

# XXX: stages
def bad_archive_contents(namelist):
    num_probs = contest.get_num_probs()
    acc_sol = ['prob-{:03d}.sol'.format(k) for k in range(1, num_probs + 1)]
    acc = set(acc_sol)

    if contest.can_buy():
        acc_buy = ['prob-{:03d}.buy'.format(k) for k in range(1, num_probs + 1)]
        acc = set(acc_sol + acc_buy)

    bad = [x for x in namelist if x not in acc]
    return bad

def validate_zip(form, field):
    f = field.data
    with tempfile.TemporaryFile(mode="w+b") as fp:
        f.save(fp)
        # Important: reset the stream so the file can be saved again
        f.stream.seek(0)
        try:
            z = zipfile.ZipFile(fp)
            ret = z.testzip()
            if ret is not None:
                raise ValidationError('The ZIP archive is corrupt: first bad file is {}.'.format(ret))
         
            fn = z.namelist()
            tlds = top_level_dirs(fn)
            if len(tlds) > 0:
                raise ValidationError('The ZIP archives a directory rather than the solution files directly. Disallowed: {}'.format(tlds))

            bad = bad_archive_contents(fn)
            if len(bad) != 0:
                raise ValidationError('ZIP not in the required format. Disallowed contents: {}'.format(bad))
        # One of the sub-exceptions in the try-block
        except ValidationError as ve:
            raise ve
        except zipfile.BadZipfile:
            raise ValidationError('File has .zip extension, but is not a ZIP file.')

class SubmitForm(FlaskForm):
    private_id = StringField('Private ID', validators=[no_redundant_spaces, priv_id_exists])
    file = FileField('Solution ZIP file', validators=[FileRequired(), FileAllowed(['zip'], 'Please upload a file with .zip extension.'), validate_zip])
    submit = SubmitField('Send submission')

class LambdaSubmitForm(FlaskForm):
    private_id = StringField('Private ID', validators=[no_redundant_spaces, priv_id_exists])
    block_num = IntegerField('Block number')
    solution = FileField('Solution file', validators=[FileRequired(), FileAllowed(['sol'], 'Task solutions must have a .sol extension.')])
    puzzle = FileField('Puzzle file', validators=[FileRequired(), FileAllowed(['desc'], 'Puzzle solutions must have a .desc extension.')])
    submit = SubmitField('Send submission')
