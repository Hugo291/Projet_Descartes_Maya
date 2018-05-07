import os

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from sqlalchemy import or_
from wtforms import IntegerField, validators, StringField, SelectField
from wtforms.validators import InputRequired, Length
from app.models.DataBase import Language
from app.config import TMP_DIR, UPLOAD_DIR_PDF


class ScanDocumentForm(FlaskForm):
    filePdf = FileField(label="File", validators=[FileRequired(message='A pdf file is required !'),
                                                  FileAllowed(['pdf'], 'Pdf only!!')])
    file_range_start = IntegerField(validators=[validators.NumberRange(min=0, max=500)], label="Start")
    file_range_end = IntegerField(validators=[validators.NumberRange(min=0, max=500)], label="End")

    def __init__(self, *arg, **kwarg):
        self.has_range = False
        self.num_page = None
        self.tmp_file_name = None
        super().__init__()

    def validate_on_submit(self):
        """

        :return: bool True if os
        """
        if not super().validate_on_submit():
            return False

        from random import randint
        from app.models import Pdf

        self.tmp_file_name = ''
        for _ in range(10):
            self.tmp_file_name += str(randint(0, 9))

        # path tmp file
        self.tmp_file_name += self.filePdf.data.filename
        tmp_path = os.path.join(TMP_DIR, str(self.tmp_file_name))
        self.filePdf.data.save(tmp_path)

        # get number page
        self.num_page = int(Pdf.page_number(path_pdf_file=tmp_path))

        # if digits equal to 0
        if int(self.file_range_start.data) == int(self.file_range_end.data) == 0:
            return True

        self.has_range = True

        # Check if min is higher than max
        if int(self.file_range_start.data) > int(self.file_range_end.data) or int(self.file_range_start.data) < 1:
            self.errors['range'] = ['The min can\'t be higher than max and start min by 1']
            return False

        # ckeck if max is higher than number pdf's page

        if self.num_page < self.file_range_end.data:
            self.errors['range'] = ['The max can\' be higher than the max of pdf\'s page']
            return False

        return True

    def save(self, name):
        """
        Move file from tmp to uplaod/pdf
        :param name: the name of file example : filename.pdf
        """
        import shutil

        shutil.move(os.path.join(TMP_DIR, self.tmp_file_name), os.path.join(UPLOAD_DIR_PDF, self.tmp_file_name))
        os.rename(os.path.join(UPLOAD_DIR_PDF, self.tmp_file_name), os.path.join(UPLOAD_DIR_PDF, str(name) + ".pdf"))

        self.close()

    def close(self):
        """
        Remove tmp file
        """
        try:
            os.remove(os.path.join(TMP_DIR, self.tmp_file_name))
        except Exception as error:
            # print("File Form.py function : close -> " + str(error))
            pass


class EditNameFileForm(FlaskForm):
    filename = StringField(validators=[InputRequired(), Length(min=2, max=200)], label="Filename")


class CreateWordForm(FlaskForm):
    lang_1 = SelectField(validators=[InputRequired()], choices=Language.get_all_language(), coerce=int,
                         label='Select Language :')
    lang_2 = SelectField(validators=[InputRequired()], choices=Language.get_all_language(), coerce=int,
                         label='Select Language :')
    text_word_1 = StringField(validators=[InputRequired()])
    text_word_2 = StringField(validators=[InputRequired()])

    def validate_on_submit(self):
        """

        :return: bool
        """
        if not super().validate_on_submit():
            return False

        # ckeck if lang in bdd

        if Language.query.filter(Language.id == self.lang_1.data).first() is None:
            self.errors['Lang'] = "It's required to choice a language"
            print("It's required to choice a language (lang1)")
            return False

        if Language.query.filter(Language.id == self.lang_2.data).first() is None:
            self.errors['Lang'] = "It's required to choice a language"
            print("It's required to choice a language (lang2)")
            return False

        # todo ckeck if is the same that in pdf table

        return True


class SelectLangForm(FlaskForm):
    lang = SelectField(validators=[InputRequired()], choices=Language.get_indigenous_language_select_field(),
                       coerce=int, label='Language :')

    def __init__(self):
        super().__init__()

    def validate_on_submit(self):
        """

        :return: bool
        """
        if not super().validate_on_submit():
            return False

        # select lang select by user
        lang_selected = Language.query.filter(Language.id == self.lang.data).first()

        # if lang not in bdd
        if lang_selected is None:
            self.errors['lang_id'] = ['The language not exist.']
            return False

        return True
