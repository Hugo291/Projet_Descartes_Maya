import os
import sys

from flask import Blueprint, render_template, request, jsonify, url_for, send_file, redirect
from flask_login import login_required, current_user
from sqlalchemy import asc

from app.config import UPLOAD_DIR_PDF, UPLOAD_DIR_JPG, UPLOAD_DIR_TXT
from app.models.ScannerThread import ScannerThread
from app.routes.users import admin_required

from app.models.DataBase import OCRPage, PdfFile, Language, db, OcrBoxWord, LogPdf, Word
from app.models.Form import EditNameFileForm, ScanDocumentForm, SelectLangForm, CreateWordForm
from shutil import rmtree

from sqlalchemy import desc

scan_app = Blueprint('scan_app', __name__, template_folder='../templates/scan', url_prefix='/scan')

threadScan = ScannerThread()
threadScan.start()


def add_file(file):
    threadScan.append_file(file)


def reset_all_file_not_finish():
    """
    Reset all record that not finish (put them in error)
    """

    # select all file not finish or in progress
    # files = PdfFile.query.filter(PdfFile.state == 1).all()

    # error = -1
    # for file in files:
    # LogPdf(pdf_file_id=file.id, message='Au demarage l\'analyse du fichier le fichier a été mit en erreur', type=-1)
    # file.state = -1
    # db.session.commit()

    # files = PdfFile.query.filter(PdfFile.state == 1).all()
    # for file in files :
    #     threadScan.append_file(file.id)
    #

    pass


reset_all_file_not_finish()


@scan_app.route('/', methods=['GET'])
@scan_app.route('/upload', methods=['GET'])
@login_required
@admin_required
def show():
    """
    Page for upload file
    :return: upload.html
    """
    form = ScanDocumentForm()
    return render_template('upload.html', form=form, title='Upload')


@scan_app.route('/upload', methods=['POST'])
@login_required
@admin_required
def upload():
    """
    This page allow users to upload a pdf file for to be scan by ocr
    :return: files.html
    """

    form = ScanDocumentForm()

    if form.validate_on_submit():

        file = form.filePdf.data
        pdf = PdfFile(name=file.filename, num_page=form.num_page, pdf_owner=current_user.get_id())

        # set range
        if form.has_range:
            print("set range")
            pdf.range_end = form.file_range_end.data
            pdf.range_start = form.file_range_start.data

        db.session.add(pdf)
        db.session.commit()

        # save the file
        form.save(pdf.id)

        # add file to thread for scan
        add_file(pdf.id)

        # return redirect(url_for('scan_app.files'))
        return jsonify(success='upload completed')
    else:
        form.close()
        # return str(form.errors)
        return jsonify(error=[value[0] for key, value in form.errors.items()])


@scan_app.route('/selection_extract/<int:pdf_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def selection_extract(pdf_id):
    # select all pages of pdf
    pdf_file = PdfFile.query.filter(pdf_id == PdfFile.id).first_or_404()

    # list langs
    langs = Language.get_indigenous_language()

    # form
    form = SelectLangForm()

    # context
    context = {'pdf': pdf_file, 'langs': langs, 'title': 'Selection', 'form': form }

    # POST
    if request.method == 'POST':

        if form.validate_on_submit():
            pdf_file.pdf_lang = form.lang.data
            db.session.commit()
            context.update({'success': 'The lang is updated'})
            return render_template('selectionExtract.html', **context)
        else:
            context.update({'error': 'An error has occurred'})
            form.lang.data = pdf_file.get_lang_id()
            return render_template('selectionExtract.html', **context)

    # GET
    form.lang.data = pdf_file.get_lang_id()
    return render_template('selectionExtract.html', **context)


@scan_app.route('/download/<int:pdf_id>')
@login_required
@admin_required
def download(pdf_id):
    """
    This page is for downlaod the document after correction

    :param pdf_id:
    :return: file of all text of pdf separate by -- num page --
    """

    # select the name of pdf
    pdf_file = PdfFile.query.filter_by(id=pdf_id).first_or_404()
    filename = pdf_file.name

    # create file path
    file_path = os.path.join(UPLOAD_DIR_TXT, str(filename) + '.txt')

    # create file
    f = open(file_path, "wb")

    # foreach pages
    for page in pdf_file.pages:
        f.write(("-" * 50 + "\n \t\t\t Num : " + str(int(page.num_page) + 1) + "\n" + "-" * 50 + "\n").encode(
            sys.stdout.encoding, errors='*Error*'))
        f.write(
            (str(page.text if page.text_corrector is None else page.text_corrector) + '\n').encode(sys.stdout.encoding,
                                                                                                   errors='*Error*'))
    f.close()

    # return file
    r = send_file(file_path)

    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'

    return r


@scan_app.route('/files', methods=['GET'])
@login_required
@admin_required
def files():
    """
    This page list all file in bdd
    :return: files.html
    """
    # select all files
    files = PdfFile.query.order_by(asc(PdfFile.state)).order_by(desc(PdfFile.date_upload)).all()
    return render_template('files.html', files=files, title='List files')


@scan_app.route('/images/<int:pdf_id>/<int:page_number>')
@login_required
@admin_required
def get_images(pdf_id, page_number):
    """
    Get pages in format jpg
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
@login_required
@admin_required
def get_boxs(pdf_id, page_number):
    """
    List of box and text of page of pdf
    :param pdf_id:
    :param page_number:
    :return: json list box of all word in page and text of page
    """

    # get all box of page

    page = OCRPage.query.filter_by(pdf_file_id=pdf_id, num_page=page_number).first_or_404()

    boxs = OcrBoxWord.query.filter_by(pdf_page_id=page.id).all()

    json_array = {'box': [e.serialize() for e in boxs],
                  'text': page.text if page.text_corrector is None else page.text_corrector}

    return jsonify(json_array)


@scan_app.route('/delete/<int:pdf_id>')
@login_required
@admin_required
def delete_file(pdf_id):
    """
    Delete the file on dbb
    :param pdf_id:
    :return: files.html
    """
    pdf = PdfFile.query.filter(PdfFile.id == pdf_id).first_or_404()

    try:

        db.session.delete(pdf)

        try:
            # remove pdf
            os.remove(os.path.join(UPLOAD_DIR_PDF, str(pdf_id) + '.pdf'))
        except Exception:
            pass

        try:
            # remove folder
            rmtree(os.path.join(UPLOAD_DIR_JPG, str(pdf_id)))
        except Exception:
            pass

        db.session.commit()
        return render_template('delete.html', success='success')

    except Exception as error:
        print("File : Scan.py function : delete_file -> " + str(error))
        return render_template('delete.html', error=error)


@scan_app.route('/correct/<int:pdf_id>/<int:num_page>', methods=['POST', 'GET'])
@login_required
@admin_required
def correction(pdf_id, num_page):
    """
    Correct the text of page
    :param pdf_id: the id of pdf
    :param num_page: the page of pdf
    :return: success or error
    """
    try:
        ocr_page = OCRPage.query.filter_by(pdf_file_id=pdf_id, num_page=num_page).first_or_404()
        ocr_page.text_corrector = request.form['text']
        db.session.commit()
        return jsonify(success='success')
    except Exception:
        return jsonify(error='error')


@scan_app.route('/details/<int:pdf_id>')
@login_required
@admin_required
def details(pdf_id):
    pdf_file = PdfFile.query.filter_by(id=pdf_id).first_or_404()
    last_logs = LogPdf.query.filter_by(pdf_file_id=pdf_file.id).order_by(desc(LogPdf.id)).limit(5)

    return render_template('details.html', pdf_file=pdf_file, last_logs=last_logs)


@scan_app.route('/pdf/<int:pdf_id>')
@login_required
@admin_required
def pdf(pdf_id):
    file_path = os.path.join(UPLOAD_DIR_PDF, str(pdf_id) + '.pdf')
    return send_file(file_path)


@scan_app.route('/edit/<int:pdf_id>', methods=["GET", "POST"])
@login_required
@admin_required
def edit(pdf_id):
    pdf = PdfFile.query.filter_by(id=int(pdf_id)).first_or_404()
    form = EditNameFileForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            pdf.name = form.filename.data
            db.session.commit()
            return render_template('edit.html', success='Filename has been successfully changed')
        else:
            return render_template('edit.html', form=form, error=[value for key, value in form.errors.items()],
                                   current_filename=pdf.name)
    else:
        return render_template('edit.html', form=form, current_filename=pdf.name)


@scan_app.route('/progress')
@login_required
@admin_required
def files_progress():
    files = PdfFile.query.all()
    return jsonify(files=[file.serialize() for file in files])


@scan_app.route('/selection_language/<int:pdf_id>')
@login_required
@admin_required
def selection_language(pdf_id):
    pdf = PdfFile.query.filter(pdf_id == PdfFile.id).first_or_404()
    langs = Language.query.all()
    form = CreateWordForm()

    form.lang_1.data = 1
    form.lang_2.data = pdf.get_lang_id()

    return render_template('selectionLangue.html', pdf=pdf, lang_select_list=langs, form=form, title='Selection Langue')


@scan_app.route('/add_word', methods=['POST'])
@login_required
@admin_required
def word():
    form = CreateWordForm()
    if form.validate_on_submit():
        new_word = Word(writer=current_user.get_id(),
                        word_es=" ".join(form.text_word_1.data.split()),
                        word_ot=" ".join(form.text_word_2.data.split()),
                        lang=form.lang_2.data
                        )
        db.session.add(new_word)
        db.session.commit()
        return jsonify(success='The word was adding in dictionary')
    else:
        return jsonify(error='Error during adding a word in dictionary')
