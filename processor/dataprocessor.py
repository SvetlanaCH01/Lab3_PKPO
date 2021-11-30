from abc import ABC, abstractmethod     # подключаем инструменты для создания абстрактных классов
import pandas   # библиотека для работы с датасетами
import os

"""
    В данном модуле реализуются классы обработчиков для 
    применения алгоритма обработки к различным типам файлов (csv или txt).
    
    ВАЖНО! Если реализация различных обработчиков занимает большое 
    количество строк, то необходимо оформлять каждый класс в отдельном файле
"""

# Родительский класс для обработчиков файлов
class DataProcessor(ABC):
    def __init__(self, datasource):
        # общие атрибуты для классов обработчиков данных
        self._datasource = datasource   # путь к источнику данных
        self._dataset = None            # входной набор данных
        self.result = None              # выходной набор данных (результат обработки)
        self._ds_shape = None
        self.dataset_final = None
        self.items_col = None
        self.dataset_in = None
        self.result1 = None 
        self.result2 = None  

    # Метод, инициализирующий источник данных
    # Все методы, помеченные декоратором @abstractmethod, ОБЯЗАТЕЛЬНЫ для переобределения
    @abstractmethod
    def read(self) -> bool:
        pass

    # Точка запуска методов обработки данных
    @abstractmethod
    def run(self):
        pass

    """
        Пример одного из общих методов обработки данных.
        В данном случае метод просто сортирует входной датасет по значению заданной колонки (аргумент col)
        
        ВАЖНО! Следует логически разделять методы обработки, например, отдельный метод для сортировки, 
        отдельный метод для удаления "пустот" в датасете и т.д. Это позволит гибко применять необходимые
        методы при переопределении метода run для того или иного типа обработчика.
        НАПРИМЕР, если ваш источник данных это не файл, а база данных, тогда метод сортировки будет не нужен,
        т.к. сортировку можно сделать при выполнении SQL-запроса типа SELECT ... ORDER BY...
    """
    

    # Абстрактный метод для вывоа результата на экран
   # @abstractmethod
    


# Реализация класса-обработчика csv-файлов
class CsvDataProcessor(DataProcessor):
    # Переобпределяем конструктор родительского класса
    def __init__(self, datasource):
        DataProcessor.__init__(self, datasource)    # инициализируем конструктор родительского класса для получения общих атрибутов
        self.separator = ';'        # дополнительный атрибут - сепаратор по умолчанию
        self.dataset_transformed1 = []
        self.dataset_transformed = []
        self.result1 = [1,2] 
    """
        Переопределяем метод инициализации источника данных.
        Т.к. данный класс предназначен для чтения CSV-файлов, то используем метод read_csv
        из библиотеки pandas
    """
    def read(self):
        self._dataset = pandas.read_csv(self._datasource, sep=self.separator, header='infer', names=None, encoding="utf-8")
        f = open(self._datasource, "w")
        f.truncate()
        f.close()
        # Читаем имена колонок из файла данных
        
        # pandas.set_option("display.max_rows", None, "display.max_columns", None)
        self._ds_shape = self._dataset.shape
        self.items_sep = ','
        self.dataset_final = pandas.DataFrame({ 'Items': [], 'Support': []})
        self.items_col='ITEM'
        col_names = self._dataset.columns
        col_id, col_item = self._dataset.columns.values
        ind = 0
        itemset = ""
        self.dataset_transformed1.append({ col_id: self._dataset.iloc[0][col_id], col_item: itemset})
        for index, row in self._dataset.iterrows():
            if row[col_id] == self.dataset_transformed1[ind][col_id]:
                itemset += row[col_item] + ","
            else:
                self.dataset_transformed1[ind][col_item] = itemset[:-1]
                ind += 1
                itemset = row[col_item] + ","
                self.dataset_transformed1.append({ col_id: row[col_id], col_item: itemset})
        self.dataset_transformed1[len(self.dataset_transformed1)-1][col_item] = itemset[:-1]
        self.dataset_transformed=pandas.DataFrame(self.dataset_transformed1)
        return True
        

   
    def run(self):
        self.dataset_in = self.dataset_transformed
        self._ds_shape =  self.dataset_transformed.shape
        self.get_ds_support(1)
       

    

    def get_ds_support(self, min_supp):
        items_set = self.dataset_in[self.items_col].str.split(self.items_sep)
        # Первый набор items для проверки.
        # Содержит списки, в которых находится по одному уникальному item
        candidates = self._get_items_ser2(items_set)
        print("First candidates:")
        print(candidates)
        candidates.to_csv('candidates.csv', index=True, sep=";", encoding="utf-8-sig")

        K = 0       # Счетчик этапов генерации и обработки списков items
        while(K!=2):
            K += 1
            # Вычисляем поддержку (support) для всех наборов items в списке кандидатов (candidates)
            # и фильтруем по пороговому значению min_supp
            validset = self._proc_candidates_set(candidates, items_set, min_supp)
            print("_____Step_%d_____" % K)
            print(validset, '\n')
            # если ни один из наборов items не прошел порог поддержки (min_supp), то завершаем цикл вычислений
            if validset.empty:
                break
            # иначе добавляем проверенное множество наборов items в итоговую таблицу данных (dataset_final)
            else:
                self.dataset_final = pandas.concat([self.dataset_final, validset])
                df1 = pandas.DataFrame(validset)
                self.result1[K-1]=df1.sort_values("Support",ascending=False)
                df3=df1.sort_values("Support",ascending=False)
                df3.to_csv('result_supp{}.csv'.format(K), index=False, sep=";", encoding="utf-8-sig")
                
                print(df3, '\n')
            candidates = self._get_new_candidates(validset['Items'])

    def _proc_candidates_set(self, candset, dataset, min_supp):
        print("Processing candidates...")
        df_buf = []
        # todo: можно оптимицировать цикл под объект Series (аргумент candset)
        for value in candset:
            # todo: Самая нагруженная часть кода!
            # Стандартная итерация
            supp = self._get_itemset_cnt_iter(value, dataset)
            # Метод apply
            #supp = self._get_itemset_cnt_apply(pandas.Series(value), dataset)
            supp = self._get_support(supp)
            if supp > 2:
                df_buf.append({'Items': value, 'Support': supp})
        return pandas.DataFrame(df_buf)

    def _get_support(self, sup_cnt):
        return (sup_cnt*100)/self._ds_shape[0]
        
    def _get_itemset_cnt_iter(self, itemset, dataset):
        counter = 0
        for _, value in dataset.items():
            # Если множество кандидатов является подмножеством в текущем наборе, то увеличиваем счетчик
            if set(itemset).issubset(value):
                counter += 1
        return counter
        
    def _get_itemset_cnt_apply(self, itemset, dataset):
        return dataset.apply(lambda row: self._is_subset(itemset, row)).sum()
        
    def _get_items_ser2(self, itemset):
        items_list = []
        # Все наборы items из dataset добавляем в общий список
        for index, value in itemset.items():
            items_list += value
        # Конвертируем полученный список в объект Series и оставляем только уникальные значения (drop_duplicates)
        # todo: здесь можно выподнить преобразование уникальных строковых значений item в числовые
        result_ser = pandas.Series(items_list).drop_duplicates().reset_index(drop=True)
        # Преобразуем каждый item в наборе в формат [item] (объект List) для возможности добавление новых item
        for index, value in result_ser.items():
            result_ser[index] = [value]
        return result_ser

    # Комбинируем items, которые прошли порог поддержки min_supp
    def _get_new_candidates(self, candset_old):
        print("Generating candidates...")
        candset_new = []    # список для хранения новых комбинаций items
        # в текущем списке множеств-кандидатов построчно просматриваем множетства ниже по таблице
        for index, val in candset_old.items():
            i = index + 1
            # если вышли за пределы таблицы, прерываем цикл
            if i >= candset_old.size:
                break
            # todo: здесь можно использовать рекуррентную функцию
            # иначе проверяем: содержится ли в текущем множестве (val) последний элемент из нижестоящего множества
            for _, subval in candset_old.iloc[i:].items():
                cand_new = list(val) # копируем список val
                sval = subval[-1]
                # если не содержится, то добавляем этот элемент к текущему множеству и получаем новое множество-кандидат
                if sval not in cand_new:
                    cand_new.append(subval[-1])
                    candset_new.append(cand_new)
        return pandas.Series(candset_new).reset_index(drop=True)
    """
class TxtDataProcessor(DataProcessor):
    # Реализация метода для чтения TXT-файла
    def read(self):
        try:
            self._dataset = pandas.read_table(self._datasource, sep='\s+', engine='python')
            col_names = self._dataset.columns
            if len(col_names) < 2:
                return False
            return True
        except Exception as e:
            print(str(e))
            return False

    def run(self):
        self.result = self.sort_data_by_col(self._dataset, "LKG", True)
        
    def print_result(self):
        print('Running TXT-file processor!\n', self.result)
        """