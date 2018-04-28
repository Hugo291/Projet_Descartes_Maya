from flask_wtf import FlaskForm, Form
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import IntegerField, validators


class ScanDocumentForm(FlaskForm):
    filePdf = FileField(label="File", validators=[FileRequired(), FileAllowed(['pdf'], 'Pdf only!!')])
    file_range_min = IntegerField(validators=[validators.NumberRange(min=0, max=500)], label="Start")
    file_range_max = IntegerField(validators=[validators.NumberRange(min=0, max=500)], label="End")

    def __init__(self, *arg, **kwarg):
        self.has_range = False
        super().__init__()

    def validate_on_submit(self):

        if not super().validate_on_submit():
            return False

        # if digits equal to 0
        if int(self.file_range_min.data) == int(self.file_range_max.data) == 0:
            return True

        self.has_range = True


        # Check if min is higher than max
        if int(self.file_range_min.data) > int(self.file_range_max.data):
            self.errors['range'] = 'The min can\'t be higher than max'
            return False

        print(self.filePdf.data.stream)
        # ckeck if max is higher than number pdf's page
        from app.models import Pdf

        # if int(Pdf.page_number(stream_pdf_file=self.filePdf.data.stream)) < self.file_range_max.data:
        #     self.errors['range'] = 'The max can\' be higher than the max of pdf\'s page'
        #     return False

        return True
