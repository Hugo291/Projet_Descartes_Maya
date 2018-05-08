import os

DEBUG = True

SECRET_KEY = 'mysecret'

#SQLAlchemy settings
#SQLALCHEMY_DATABASE_URI = 'mysql://descartes_gama:lpinfo@mysql-descartes.alwaysdata.net/descartes_mexique2'
#SQLALCHEMY_DATABASE_URI = 'mysql://158403:12345@mysql-descartes-ocr.alwaysdata.net/descartes-ocr_final'
SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/descartes-ocr_final'
#SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/descartes-presentation'

SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids a SQLAlchemy Warning

# Static
STATIC = 'static'

# Mail
MAIL_SERVER = 'smtp-descartes.alwaysdata.net'
MAIL_USERNAME = 'descartes@alwaysdata.net'
MAIL_PASSWORD = 'lpinfo'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USE_TLS = False

# UPLOAD FILE SETTINGS

ALLOW_EXTENSION_FILE_UPLOAD = 'Pdf'

CURRENT_DIR = os.getcwd()

PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR))
CURRENT_DIR = os.getcwd()

UPLOAD_DIR_NAME = "upload"
UPLOAD_DIR_NAME = os.path.join('app', UPLOAD_DIR_NAME)

TMP_DIR_NAME = "tmp"
TMP_DIR = os.path.join('app', TMP_DIR_NAME)
TMP_DIR = os.path.join(CURRENT_DIR, TMP_DIR)

UPLOAD_DIR = os.path.join(PARENT_DIR, UPLOAD_DIR_NAME)

UPLOAD_DIR_PDF = os.path.join(UPLOAD_DIR, "pdf")
UPLOAD_DIR_JPG = os.path.join(UPLOAD_DIR, "jpg")
UPLOAD_DIR_TXT = os.path.join(UPLOAD_DIR, "txt")

UPLOAD_DIR_PDF_FILE = os.path.join(UPLOAD_DIR_PDF, 'file')
UPLOAD_DIR_PDF_PAGES = os.path.join(UPLOAD_DIR_PDF, 'pages')

# crsf enabled
WTF_CSRF_ENABLED = False

# File upload
MAX_CONTENT_LENGTH = 100000 * 1024 * 1024
