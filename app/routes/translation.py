from flask import Flask
from flask import Blueprint, render_template
from flask_login import login_required

from app.models.DataBase import Language, Word

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


@translation_app.route('/languages')
@login_required
def languages():
    langs = Language.get_indigenous_language()
    return render_template('languages.html', languages=langs)


@translation_app.route('/dictionary/<int:lang_id>')
@login_required
def dictionary(lang_id):
    lang = Language.query.filter(Language.id == lang_id).first_or_404()
    words = Word.query.filter(Word.lang == lang_id).all()
    return render_template('dictionary.html', lang=lang, words=words)
