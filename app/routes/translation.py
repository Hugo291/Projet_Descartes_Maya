from flask import Flask
from flask import Blueprint, render_template
from flask_login import login_required

translation_app = Blueprint('translation_app', __name__, template_folder='../templates/translation')

@translation_app.route("/search_a_translation")
@login_required
def search_translation():
    return render_template('translation/search_translation.html', title='Search')


@translation_app.route("/translate_word")
@login_required
def translate_word():
    return render_template('translation/translate_word.html', title='Translate a word')


@translation_app.route("/untranslated_words")
@login_required
def untranslated_words():
    return render_template('translation/untranslated_words.html', title='List of untranslated words')


@translation_app.route("/import_words_PDF")
@login_required
def import_words_PDF():
    return render_template('import_words_PDF.html')


@translation_app.route("/add_words_from_PDF")
@login_required
def add_words_from_PDF():
    return render_template('add_words_from_PDF.html')