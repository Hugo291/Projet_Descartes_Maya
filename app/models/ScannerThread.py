import os
import time
from threading import Thread

from app.config import UPLOAD_DIR_PDF, UPLOAD_DIR_JPG
from app.models.OCR import OCR
from app.models.Pdf import convert_to_jpg, page_number
from app.models.DataBase import LogPdf

cal = lambda current, total: int((current + 1) * 100 / total)


class ScannerThread(Thread):

    def __init__(self):
        """
        Construct
        """
        super().__init__()
        self.__list_file = []
        self.__percent = 0

    def run(self):
        """
        Loop infinit and if detect a file in list , the
        """
        super().run()
        while True:
            time.sleep(10)
            while self.has_waiting_file():
                self.set_percent(0)
                self.convert_scan_file()
                self.delete_last_file_scaned()
                self.set_percent(0)

    def has_waiting_file(self):
        """
         Return True if a file is in list
        :return: bool
        """
        if len(self.__list_file) != 0:
            return True
        return False

    def get_last_file_scaned(self):
        """
        :return: the last or current file which has been scanned
        """
        return self.__list_file[0]

    def delete_last_file_scaned(self):
        """Thread init
            Delete the last file to be scan
        """
        del self.__list_file[0]

    def append_file(self, pdf_file_id):
        """
        Add the file to the list of files that will be scanned
        :param pdf_file_id: the pdf id
        """
        print("The file n° " + str(pdf_file_id) + " is add to thread")
        self.__list_file.append(pdf_file_id)

    def convert_scan_file(self):
        """
        Convert the file and scan this
        """
        from app.models.DataBase import PdfFile, OcrBoxWord, OCRPage, db, LogPdf

        # pdf file bd
        pdf_file_db = PdfFile.query.filter_by(id=self.get_last_file_scaned()).first()
        # the page  number pdf
        folder_jpg = os.path.join(UPLOAD_DIR_JPG, str(self.get_last_file_scaned()))
        file_path = os.path.join(UPLOAD_DIR_PDF, str(self.get_last_file_scaned()) + ".pdf")

        try:

            # set state In progress
            pdf_file_db.state = 1

            range_start, range_end = pdf_file_db.get_range

            for index in range(range_start, range_end):

                self.log('Start of the convert process of page n°{0}'.format(str(index)))

                convert_to_jpg(file_path, folder_jpg, num_page=index)

                path_file_img = os.path.join(folder_jpg, '{0}.jpg'.format(str(index)))

                self.log(
                    'Convert process of page n°{0} completed .Picture of the page available at this link -> {1}'.format(
                        index, path_file_img))

                image_ocr = OCRPage(pdf_file_id=self.get_last_file_scaned(), num_page=index)

                self.log('Start of scanning process of file n°{0}'.format(str(index)))

                scanner_ocr = OCR(path_file_img)
                image_ocr.text = scanner_ocr.scan_text()

                self.log('End of the scanning process of file n°{0}'.format(str(index)))

                db.session.add(image_ocr)
                db.session.commit()

                id_pdf_page = image_ocr.id

                self.log('Start of the box recovering process from page n°{0}'.format(str(index)))

                box_word = scanner_ocr.scan_data()

                for box in box_word:
                    box_word = OcrBoxWord(pdf_page_id=id_pdf_page, box=box)
                    db.session.add(box_word)

                # commit all word box in folder
                db.session.commit()

                self.log('End of the box recovering process from page n°{0}'.format(str(index)))

                print("Page num °" + str(index) + " finished ")

                self.set_percent(int(cal(current=index, total=range_end - range_start)))

            # set staus finish

            pdf_file_db.state = 2
            db.session.commit()

            self.log('File analysed with success', type=1)

            print("The file is finish")

        except Exception as error:
            print("function : convert_scan_file -> " + str(error))
            pdf_file_db.state = -1
            db.session.commit()
            self.log('An exception raised during the process -> ' + str(error), type=-1)

    def __str__(self):
        return str(self.get_percent)

    def get_percent(self):
        return self.__percent

    def set_percent(self, percent):
        """
        :param percent:
        """
        print("File : " + str(self.__percent) + " %")
        self.__percent = percent

    def log(self, message, type=0):
        LogPdf(pdf_file_id=self.get_last_file_scaned(), message=message, type=type)


    def get_file_progress(self, pdf_id):
        if pdf_id is self.get_last_file_scaned():
            return self.get_percent()
        else:
            return 0
