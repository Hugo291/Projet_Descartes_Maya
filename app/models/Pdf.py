import os

from pdf2image import pdf2image
from PyPDF2 import PdfFileReader


def page_number(path_pdf_file=None, stream_pdf_file=None):
    """
    return the pages number of pdf
    :param path_pdf_file:  path of pdf file
    :param stream_pdf_file: stream of pdf file
    :return: number of pages in pdf
    """
    if path_pdf_file is not None:
        f = open(path_pdf_file, 'rb')
        num = PdfFileReader(f, strict=False).getNumPages()
        f.close()
        return num
    num = PdfFileReader(stream_pdf_file).getNumPages()
    return num


def convert_to_jpg(input_pdf_file, target_dir, num_page=0, fname_fmt="{num_page}.jpg"):
    """
    Convert a page of a pdf in jpg
    :param input_pdf_file: pdf path
    :param target_dir: the dest of images
    :param num_page: the page number to convert
    :param fname_fmt: the dest name
    """
    if not os.path.exists(target_dir):
        # create folder if not exist
        os.makedirs(target_dir)

    images = pdf2image.convert_from_path(input_pdf_file, first_page=num_page + 1, last_page=num_page + 2)

    path_file = os.path.join(target_dir, fname_fmt.format(num_page=num_page))
    images[0].save(path_file)
