import os

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import IntegerField, validators

from app.config import TMP_DIR, UPLOAD_DIR_PDF


class ScanDocumentForm(FlaskForm):
    filePdf = FileField(label="File", validators=[FileRequired(), FileAllowed(['pdf'], 'Pdf only!!')])
    file_range_min = IntegerField(validators=[validators.NumberRange(min=0, max=500)], label="Start")
    file_range_max = IntegerField(validators=[validators.NumberRange(min=0, max=500)], label="End")

    def __init__(self, *arg, **kwarg):
        self.has_range = False
        self.num_page = None
        self.tmp_file_name = None
        super().__init__()

    def validate_on_submit(self):

        if not super().validate_on_submit():
            return False

        from random import randint
        from app.models import Pdf

        self.tmp_file_name = ''
        for _ in range(10):
            self.tmp_file_name += str(randint(0, 9))

        self.tmp_file_name += self.filePdf.data.filename

        tmp_path = os.path.join(TMP_DIR, str(self.tmp_file_name))
        self.filePdf.data.save(tmp_path)

        self.num_page = int(Pdf.page_number(path_pdf_file=tmp_path))

        # if digits equal to 0
        if int(self.file_range_min.data) == int(self.file_range_max.data) == 0:
            return True

        self.has_range = True

        # Check if min is higher than max
        if int(self.file_range_min.data) > int(self.file_range_max.data):
            self.errors['range'] = 'The min can\'t be higher than max'
            return False

        # ckeck if max is higher than number pdf's page

        if self.num_page < self.file_range_max.data:
            self.errors['range'] = 'The max can\' be higher than the max of pdf\'s page'
            return False

        return True

    def save(self, name):

        import shutil

        shutil.move(os.path.join(TMP_DIR, self.tmp_file_name), os.path.join(UPLOAD_DIR_PDF, self.tmp_file_name))
        os.rename(os.path.join(UPLOAD_DIR_PDF, self.tmp_file_name), os.path.join(UPLOAD_DIR_PDF, str(name)+".pdf"))
