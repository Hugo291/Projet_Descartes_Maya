import datetime

from app import db
from app.models.userModels import User

"""
    This table is for save the name and path of file
"""

PDF_ERROR = -1
PDF_SUCCESS = 2
PDF_IN_PROGRESS = 1
PDF_WAIT = 0


class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(100), nullable=False)

    def __int__(self, name):
        self.name = name

    def __str__(self):
        return 'Langue : ' + str(self.name)

    @staticmethod
    def get_indigenous_language():
        return Language.query.filter((Language.id != 1)).all()

    @staticmethod
    def get_indigenous_language_select_field():
        return [(0, 'Not defined'), ] + [(lang.id, lang.language) for lang in Language.get_indigenous_language()]

    @staticmethod
    def get_all_language():
        return [(0, 'Not defined'), ] + [(lang.id, lang.language) for lang in Language.query.all()]


class PdfFile(db.Model):
    __tablename__ = 'pdf_file'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    state = db.Column(db.Integer, default=0)
    pdf_owner = db.Column(db.Integer, db.ForeignKey(User.id, ondelete='SET NULL'), nullable=True)
    pdf_lang = db.Column(db.Integer, db.ForeignKey(Language.id, ondelete='CASCADE'), nullable=True)
    range_start = db.Column(db.Integer)
    range_end = db.Column(db.Integer)
    num_page = db.Column(db.Integer)
    date_upload = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    owner = db.relationship('User')
    pages = db.relationship('OCRPage', cascade="all, delete-orphan")
    logs = db.relationship('LogPdf', cascade="all, delete-orphan")
    lang = db.relationship('Language')

    def __init__(self, id=None, name=None, num_page=None, pdf_owner=None):
        self.id = id
        self.name = name
        self.num_page = num_page
        self.pdf_owner = pdf_owner

    def __str__(self):
        return 'id : ' + str(self.id) + ' name : ' + str(self.name) + " Range start/end : " + str(
            self.range_start) + "/" + str(self.range_end)

    def has_range(self):
        var = False if self.range_end is None and self.range_start is None else True
        return var

    def get_range(self):
        if self.range_start is None and self.range_end is None:
            return 0, self.num_page
        else:
            return self.range_start - 1, self.range_end

    def serialize(self):
        from app.routes.scan import threadScan
        from app.template_filter.ValueStatus import value_status_file
        return {
            'id': self.id,
            'progress': threadScan.get_file_progress(pdf_id=self.id),
            'state': self.state,
            'html_status': value_status_file(self.state)
        }

    def get_lang_id(self):
        if self.lang is None:
            return 0
        else:
            return self.lang.id


class LogPdf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pdf_file_id = db.Column(db.Integer, db.ForeignKey(PdfFile.id, ondelete='CASCADE'), nullable=False)
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    message = db.Column(db.Text, nullable=True)
    type = db.Column(db.Integer, default=0)

    def __init__(self, pdf_file_id, message, type=0):
        self.pdf_file_id = pdf_file_id
        self.message = message
        self.type = type

        db.session.add(self)
        db.session.commit()


class OCRPage(db.Model):
    __tablename__ = 'ocr_page'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pdf_file_id = db.Column(db.Integer, db.ForeignKey(PdfFile.id, ondelete='CASCADE'), nullable=False)
    num_page = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=True)
    text_corrector = db.Column(db.Text, nullable=True)

    def __init__(self, id=None, pdf_file_id=None, num_page=None, text=None):
        self.id = id
        self.pdf_file_id = pdf_file_id
        self.num_page = num_page
        self.text = text


class OcrBoxWord(db.Model):
    __tablename__ = 'ocr_box_word'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pdf_page_id = db.Column(db.Integer, db.ForeignKey(OCRPage.id, ondelete='CASCADE'), nullable=False)
    size_width = db.Column(db.Integer)
    size_height = db.Column(db.Integer)
    position_top = db.Column(db.Integer)
    position_left = db.Column(db.Integer)
    text = db.Column(db.Text)

    def __init__(self,
                 id=None,
                 pdf_page_id=None,
                 size_width=None,
                 size_height=None,
                 position_top=None,
                 position_left=None,
                 text=None, box=None):
        self.id = id
        self.pdf_page_id = pdf_page_id
        self.size_height = size_height
        self.size_width = size_width
        self.text = text
        self.position_left = position_left
        self.position_top = position_top

        if box is not None:
            self.size_height = box['height'],
            self.size_width = box['width'],
            self.position_top = box['top'],
            self.position_left = box['left'],
            self.text = box['text']

    def serialize(self):
        return {
            'id': self.id,
            'pdf_page_id': self.pdf_page_id,
            'size_height': self.size_height,
            'size_width': self.size_width,
            'text': self.text,
            'position_left': self.position_left,
            'position_top': self.position_top,
        }

    def __str__(self):
        return '__str__'


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    writer = db.Column(db.Integer, db.ForeignKey(User.id, ondelete='SET NULL'), nullable=True)
    word_es = db.Column(db.String(200), nullable=False)
    word_ot = db.Column(db.String(200), nullable=False)
    lang = db.Column(db.Integer, db.ForeignKey(Language.id, ondelete='CASCADE'), nullable=True)

    def __init__(self, writer, word_es, word_ot, lang):
        self.writer = writer
        self.word_es = word_es
        self.word_ot = word_ot
        self.lang = lang


class SelectWordPos(db.Model):
    __tablename__ = 'select_word_pos'
    id = db.Column(db.Integer, primary_key=True)
    pos_start = db.Column(db.Integer, nullable=True)
    pos_end = db.Column(db.Integer, nullable=True)
    word = db.Column(db.Integer, db.ForeignKey(Word.id, ondelete='SET NULL'), nullable=True)

    def __init__(self, pos_start, pos_end, word):
        self.pos_end = pos_end
        self.pos_start = pos_start
        self.word = word
