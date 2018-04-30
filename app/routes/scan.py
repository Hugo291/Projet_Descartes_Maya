import os
import sys

from flask import Blueprint, render_template, request, jsonify, url_for, send_file, redirect
from sqlalchemy import asc

from app.config import UPLOAD_DIR_PDF, UPLOAD_DIR_JPG, UPLOAD_DIR_TXT
from app.models.ScannerThread import ScannerThread

scan_app = Blueprint('scan_app', __name__, template_folder='../templates/scan', url_prefix='/scan')

threadScan = ScannerThread()
threadScan.start()


def add_file(file):
    threadScan.append_file(file)


def reset_all_file_unfinish():
    """
    Reset all record that not finish (put them in error)
    """
    from app.models.DataBase import PdfFile, db, LogPdf

    # select all file not finish or in progress
    files = PdfFile.query.filter((PdfFile.state == 0) | (PdfFile.state == 1)).all()

    # error = -1
    for file in files:
        LogPdf(pdf_file_id=file.id, message='Au demarage l\'analyse du fichier le fichier a été mit en erreur', type=-1)
        file.state = -1

    db.session.commit()


reset_all_file_unfinish()


@scan_app.route('/', methods=['GET'])
@scan_app.route('/upload', methods=['GET'])
def show():
    """
    Page for uplaod file
    :return: upload.html
    """
    from app.models.Form import ScanDocumentForm
    form = ScanDocumentForm()
    return render_template('upload.html', form=form, title='Uplaod')


@scan_app.route('/upload', methods=['POST'])
def upload():
    """
    This page allow users to upload a pdf file for to be scan by ocr
    :return: files.html
    """
    from app.models.Form import ScanDocumentForm

    form = ScanDocumentForm()

    if form.validate_on_submit():

        from app.models.DataBase import PdfFile, db

        file = form.filePdf.data

        pdf = PdfFile(name=file.filename, num_page=form.num_page)

        # set range
        if form.has_range:
            print("set range")
            pdf.range_max = form.file_range_max.data
            pdf.range_min = form.file_range_min.data

        db.session.add(pdf)
        db.session.commit()

        # save the file
        form.save(pdf.id)

        # add file to thread for scan
        add_file(pdf.id)

        return redirect(url_for('scan_app.files'))
    else:
        form.close()
        return str(form.errors)


@scan_app.route('/selectionExtract/<int:pdf_id>', methods=['GET', 'POST'])
def selection_extract(pdf_id):
    from app.models.DataBase import OCRPage
    try:
        # select all pages of pdf
        pages = OCRPage.query.filter_by(pdf_file_id=pdf_id).all()

        return render_template('selectionExtract.html', pages=pages, pdf_id=pdf_id, title='Selection')
    except Exception as E:
        return str(E)


@scan_app.route('/downlaod/<int:pdf_id>')
def download(pdf_id):
    """
    This page is for downlaod the document after correction

    :param pdf_id:
    :return: file of all text of pdf separate by -- num page --
    """
    from app.models.DataBase import OCRPage, PdfFile

    # select the name of pdf
    pdf_file = PdfFile.query.filter_by(id=pdf_id).first()
    filename = pdf_file.name

    # create file path
    file_path = os.path.join(UPLOAD_DIR_TXT, str(filename) + '.txt')

    # select all pages of pdf
    pages = OCRPage.query.filter_by(pdf_file_id=str(pdf_id)).all()

    # create file
    f = open(file_path, "wb")

    # foreach pages
    for page in pages:
        f.write(("-" * 50 + "\n \t\t\t Num : " + page.num_page + "\n" + "-" * 50 + "\n").encode(sys.stdout.encoding,
                                                                                                errors='*Error*'))
        f.write(
            (str(page.text if page.text_corrector is None else page.text_corrector) + '\n').encode(sys.stdout.encoding,
                                                                                                   errors='*Error*'))
    f.close()

    # return file
    return send_file(file_path)


@scan_app.route('/files', methods=['GET'])
def files():
    """
    This page list all file in bdd
    :return: files.html
    """
    from app.models.DataBase import PdfFile

    # select all files
    files = PdfFile.query.order_by(asc(PdfFile.state)).order_by(asc(PdfFile.name)).all()

    return render_template('files.html', files=files, title='List files')


@scan_app.route('/images/<int:pdf_id>/<int:page_number>')
def get_images(pdf_id, page_number):
    """

    :param pdf_id: the id of pdf
    :param page_number: page number
    :return: the image of page of pdf
    """
    # the folder of pdf
    folder = os.path.join(UPLOAD_DIR_JPG, str(pdf_id))
    # the page file name
    filename = os.path.join(folder, str(page_number) + '.jpg')
    # return the image
    return send_file(filename, mimetype='image/jpg')


@scan_app.route('/page/<int:pdf_id>/<int:page_number>')
def get_boxs(pdf_id, page_number):
    """
    List of box and text of page of pdf
    :param pdf_id:
    :param page_number:
    :return: json list box of all word in page and text of page
    """
    from app.models.DataBase import OcrBoxWord, OCRPage

    # get all box of page
    page = OCRPage.query.filter_by(pdf_file_id=pdf_id, num_page=page_number).first()

    boxs = OcrBoxWord.query.filter_by(pdf_page_id=page.id).all()

    json_array = {'box': [e.serialize() for e in boxs],
                  'text': page.text if page.text_corrector is None else page.text_corrector}

    return jsonify(json_array)


@scan_app.route('/delete/<int:pdf_id>')
def delete_file(pdf_id):
    """
    Delete the file on dbb
    :param pdf_id:
    :return: files.html
    """
    try:

        from app.models.DataBase import PdfFile, db
        PdfFile.query.filter_by(id=pdf_id).delete()

        try:
            # remove pdf
            os.remove(os.path.join(UPLOAD_DIR_PDF, str(pdf_id) + '.pdf'))
        except Exception as exception:
            print('Error during delete of pdf. ' + str(exception))

        try:
            # remove folder
            from shutil import rmtree
            rmtree(os.path.join(UPLOAD_DIR_JPG, str(pdf_id)))
        except Exception as exception:
            print('Error during delete folder jpg. ' + str(exception))

        db.session.commit()
        return redirect(url_for('scan_app.files'))

    except Exception as error:
        return jsonify({'error': 'During delete ( ' + str(error) + ' )'})


@scan_app.route('/correct/<int:pdf_id>/<int:num_page>', methods=['POST', 'GET'])
def correction(pdf_id, num_page):
    """
    Correct the text of page
    :param pdf_id: the id of pdf
    :param num_page: the page of pdf
    :return: success or error
    """
    from app.models.DataBase import OCRPage, db
    ocr_page = OCRPage.query.filter_by(pdf_file_id=pdf_id, num_page=num_page).first()
    ocr_page.text_corrector = request.form['text']
    db.session.commit()
    return 'success'


@scan_app.route('/details/<int:pdf_id>')
def details(pdf_id):
    from app.models.DataBase import PdfFile, LogPdf
    from sqlalchemy import desc

    pdf_file = PdfFile.query.filter_by(id=pdf_id).first()
    last_logs = LogPdf.query.filter_by(pdf_file_id=pdf_file.id).order_by(desc(LogPdf.id)).limit(5)

    return render_template('details.html', pdf_file=pdf_file, last_logs=last_logs)


@scan_app.route('/pdf/<int:pdf_id>')
def pdf(pdf_id):
    file_path = os.path.join(UPLOAD_DIR_PDF, str(pdf_id) + '.pdf')
    return send_file(file_path)
