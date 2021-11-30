from abc import ABC, abstractmethod
from .dataprocessor import *
import os

"""
    В данном модуле объявляются классы, реализующие фабричный метод get_processor, 
    который возвращает соответствующие классы обработчиков данных
"""

class DataProcessorFactory(ABC):
    def __init__(self):
        self.instance = None

    @abstractmethod
    def get_processor(self, datasource) -> DataProcessor:
        pass

"""
    Фабричный метод может не только возвращать класс соответствующего обработчика,
    здесь также может быть реализована логика, которая меняет поведение данного обработчика,
    например, меняет тип разделителя и кодировку для CSV-файла (через атрибуты класса),
    применяет различные режимы обработки и т.д.
"""

# Фабрика CsvDataProcessor
class CsvDataProcessorFactory(DataProcessorFactory):
    # Фабричный метод для CsvDataProcessor читает файл с сепаратором по умолчанию (;),
    # если неудачно, то читаем с сепаратором ','
    # Если все попытки чтения неудачны возвращаем None
    def get_processor(self, datasource) -> DataProcessor:
        self.instance = CsvDataProcessor(datasource)
        if self.instance.read():
            return self.instance
        elif self.read_with_separator(','):
            return self.instance
        return None

    def read_with_separator(self, sep) -> bool:
        self.instance.separator = sep
        if self.instance.read():
            return True
        return False

# Фабрика TxtDataProcessor
class TxtDataProcessorFactory(DataProcessorFactory):
    def get_processor(self, datasource) -> DataProcessor:
        self.instance = TxtDataProcessor(datasource)
        if self.instance.read():
            return self.instance
        return None