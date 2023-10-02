"""
Парсер плагина SPP

1/2 документ плагина
"""
import datetime
import logging
import os
import time

from dateutil.parser import parse
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait, Select

from src.spp.types import SPP_document


class TheBerlinGroup:
    """
    Класс парсера плагина SPP

    :warning Все необходимое для работы парсера должно находится внутри этого класса

    :_content_document: Это список объектов документа. При старте класса этот список должен обнулиться,
                        а затем по мере обработки источника - заполняться.


    """

    # Ссылки по которым должен пройтись парсер
    HOSTs = (
        'https://www.berlin-group.org/openfinance-downloads',
        'https://www.berlin-group.org/nextgenpsd2-downloads',
        'https://www.berlin-group.org/nextgenmp2p-download-page',
        'https://www.berlin-group.org/iso20022-sepa-card-clearing-downloads',
        'https://www.berlin-group.org/iso8583-authorisation-clearing-downloads',
    )

    SOURCE_NAME = 'the-berlin-group'
    _content_document: list[SPP_document]

    def __init__(self, driver):
        """
        Конструктор класса парсера

        По умолчанию внего ничего не передается, но если требуется (например: driver селениума), то нужно будет
        заполнить конфигурацию
        """

        # Логер должен подключаться так. Вся настройка лежит на платформе
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(f"Parser class init completed")
        self.logger.info(f"Set source: {self.SOURCE_NAME}")

        # Обнуление списка
        self._content_document = []

        #
        self.driver = driver
        ...

    def content(self) -> list[SPP_document]:
        """
        Главный метод парсера. Его будет вызывать платформа. Он вызывает метод _parse и возвращает список документов
        :return:
        :rtype:
        """
        self.logger.debug("Parse process start")
        with self.driver:
            for host in self.HOSTs:
                self._temp(host)
        self.logger.debug("Parse process finished")
        return self._content_document

    def _temp(self, host: str):
        # HOST - это главная ссылка на источник, по которому будет "бегать" парсер
        self.logger.debug(F"Parser enter to {host}")

        self.find_new_doc(host, 'RTP Operational Rules 1.0', datetime.datetime.strptime('20210924', '%Y%m%d'))
        self.find_new_doc(host, 'RTP Implementation Guidelines 1.0', datetime.datetime.strptime('20210924', '%Y%m%d'))
        self.find_new_doc(host, 'Payment Data Model for V2 1.0', datetime.datetime.strptime('20210924', '%Y%m%d'))
        self.find_new_doc(host, 'RTP_SCTv1_0_0__20220303', datetime.datetime.strptime('20220303', '%Y%m%d'))
        self.find_new_doc(host, 'Status Notification Implementation Guidelines 1.2', datetime.datetime.strptime('20210924', '%Y%m%d'))
        self.find_new_doc(host, 'oFA-api-status_notification v1.2.0-20211209v1', datetime.datetime.strptime('20220505', '%Y%m%d'))
        self.find_new_doc(host, 'Push Account Operational Rules 1.1', datetime.datetime.strptime('20220303', '%Y%m%d'))
        self.find_new_doc(host, 'Push Account Implementation Guidelines 1.1', datetime.datetime.strptime('20220303', '%Y%m%d'))
        self.find_new_doc(host, 'psd2-api-push_account_information v1.0-20220516', datetime.datetime.strptime('20220516', '%Y%m%d'))
        self.find_new_doc(host, 'Extended PIS Operational Rules 1.0', datetime.datetime.strptime('20220429', '%Y%m%d'))
        self.find_new_doc(host, 'Extended PIS Implementation Guidelines 1.0 ', datetime.datetime.strptime('20220429', '%Y%m%d'))
        self.find_new_doc(host, 'Securities AIS Implementation Guidelines 1.0', datetime.datetime.strptime('20221116', '%Y%m%d'))
        self.find_new_doc(host, 'Transactions Data Model V2 1.0', datetime.datetime.strptime('20230321', '%Y%m%d'))



    def find_new_doc(self, host: str, filename: str, date: datetime.datetime = datetime.datetime.now(), delay: float = 0.5):
        doc = SPP_document(None, filename, None, None, f'{host}/ugd/{filename}.pdf', None, {}, date, None)
        self._content_document.append(doc)
        self.logger.info(self._find_document_text_for_logger(doc))
        time.sleep(delay)

    def _parse(self, host: str):
        """
        Метод, занимающийся парсингом. Он добавляет в _content_document документы, которые получилось обработать
        :return:
        :rtype:
        """


        # HOST - это главная ссылка на источник, по которому будет "бегать" парсер
        self.logger.debug(F"Parser enter to {host}")

        # ========================================
        # Тут должен находится блок кода, отвечающий за парсинг конкретного источника
        # -
        self.driver.set_page_load_timeout(40)
        self.driver.get(url=host)
        time.sleep(6)

        # прохождение панели с куками
        ccc_accept = self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/button[1]')
        if WebDriverWait(self.driver, 5).until(ec.element_to_be_clickable(ccc_accept)):
            ccc_accept.click()
            self.logger.debug(F"Parser enter notify accept")

        if WebDriverWait(self.driver, 15).until(ec.frame_to_be_available_and_switch_to_it(self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div[3]/div/main/div/div/div/div[2]/div/div/div/section[1]/div[2]/div/div[5]/iframe'))):
            table = self.driver.find_element(By.XPATH, '/html/body/div/section[2]/div/div/div/table/tbody')
            row = table.find_element(By.CLASS_NAME, 'tr')
            print(row)

        time.sleep(2)




        # Логирование найденного документа
        #self.logger.info(self._find_document_text_for_logger(document))

        # ---
        # ========================================
        ...

    @staticmethod
    def _find_document_text_for_logger(doc: SPP_document):
        """
        Единый для всех парсеров метод, который подготовит на основе SPP_document строку для логера
        :param doc: Документ, полученный парсером во время своей работы
        :type doc:
        :return: Строка для логера на основе документа
        :rtype:
        """
        return f"Find document | name: {doc.title} | link to web: {doc.web_link} | publication date: {doc.pub_date}"

    @staticmethod
    def some_necessary_method():
        """
        Если для парсинга нужен какой-то метод, то его нужно писать в классе.

        Например: конвертация дат и времени, конвертация версий документов и т. д.
        :return:
        :rtype:
        """
        ...

    @staticmethod
    def nasty_download(driver, path: str, url: str) -> str:
        """
        Метод для "противных" источников. Для разных источника он может отличаться.
        Но основной его задачей является:
            доведение driver селениума до файла непосредственно.

            Например: пройти куки, ввод форм и т. п.

        Метод скачивает документ по пути, указанному в driver, и возвращает имя файла, который был сохранен
        :param driver: WebInstallDriver, должен быть с настроенным местом скачивания
        :_type driver: WebInstallDriver
        :param url:
        :_type url:
        :return:
        :rtype:
        """

        with driver:
            driver.set_page_load_timeout(40)
            driver.get(url=url)
            time.sleep(1)

            # ========================================
            # Тут должен находится блок кода, отвечающий за конкретный источник
            # -
            # ---
            # ========================================

            # Ожидание полной загрузки файла
            while not os.path.exists(path + '/' + url.split('/')[-1]):
                time.sleep(1)

            if os.path.isfile(path + '/' + url.split('/')[-1]):
                # filename
                return url.split('/')[-1]
            else:
                return ""
