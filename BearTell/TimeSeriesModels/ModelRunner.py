# -*- coding: utf-8 -*-

from Algoritmalar.model_arima import ModelArima
from Algoritmalar.model_lstm import ModelLSTM
from Algoritmalar.model_sarima import ModelSarima
from Algoritmalar.model_outlier import ModelOutlier
import math
from datetime import datetime,timedelta
from rest_framework.response import Response
import pandas as pd
import requests, json
from dateutil.relativedelta import relativedelta
from numpy import percentile
# import threading


class ModelRunner:
    def __init__(self, arguments):
        self.dataSourceType = arguments.get('dataSourceType')
        self.startDate = str(arguments.get('startDate'))
        self.endDate = str(arguments.get('endDate'))
        self.sensorName = arguments.get('sensorName')
        self.analysisType = arguments.get('analysisType')
        self.zamanDilimi = arguments.get('zamanDilimi')
        self.textZaman = arguments.get('textZaman')
        self.anomali = arguments.get('anomali')
        self.urls = []
        self.learn_data = pd.DataFrame()
        self.date_list = []
        self.step_size = None
        self.step_sec = None

    def veri_al(self):
        print('veri al calisti')
        start_date_datetime = datetime.strptime(self.startDate, '%Y/%m/%d-%H:%M:%S')  # datetime
        end_date_datetime = datetime.strptime(self.endDate, "%Y/%m/%d-%H:%M:%S")  # datetime
        if int((end_date_datetime - start_date_datetime).days) < 1:
            start = datetime.strftime(start_date_datetime, '%Y/%m/%d-%H:%M:%S') #string
            end = datetime.strftime(end_date_datetime, "%Y/%m/%d-%H:%M:%S")     #string
            url = (self.dataSourceType + "/api/query?start=" + start + "&end=" +
                   end + "&m=sum:"+self.textZaman+self.zamanDilimi+"-avg:"  + self.sensorName)
            self.urls.append(url)
        else:
            total = math.ceil((end_date_datetime - start_date_datetime).days)
            _date_temp = start_date_datetime
            for i in range(1, total, 1):
                new_start_date_string = datetime.strftime(_date_temp, '%Y/%m/%d-%H:%M:%S')
                new_end_date_datetime = _date_temp + timedelta(days=1)
                new_end_date_string = datetime.strftime(new_end_date_datetime, '%Y/%m/%d-%H:%M:%S')
                url = (self.dataSourceType + "/api/query?start=" + new_start_date_string + "&end=" + new_end_date_string
                       + "&m=sum:"+self.textZaman+self.zamanDilimi+"-avg:" + self.sensorName)
                self.urls.append(url)
                _date_temp = new_end_date_datetime
        print(self.urls)

    def duzenle(self):
        print('duzenle calisti')
        print('zaman parametresi=', self.zamanDilimi)
        print('zaman degeri=', self.textZaman)
        url_len = len(self.urls)
        dolu_veri = None
        for k in range(0, url_len, 1):
            request_data = requests.get(self.urls[k])
            if len(request_data.content) > 0:
                data = json.loads(request_data.content)
                if data != []:
                    dolu_veri = k + 1
        egitim_data = int(dolu_veri * 0.7)
        self.step_size = url_len - dolu_veri
        print("Dolu Veri: ", dolu_veri)
        print("Egitim Verisi: ", egitim_data)
        print("Adim Sayisi: ", self.step_size)

        start_date_dt = datetime.strptime(self.startDate, "%Y/%m/%d-%H:%M:%S")
        end_date_dt = datetime.strptime(self.endDate, "%Y/%m/%d-%H:%M:%S")
        start_date_dt1 = datetime.strftime(start_date_dt, "%Y/%m/%d")
        end_date_dt1 = datetime.strftime(end_date_dt, "%Y/%m/%d")
        self.startDate = start_date_dt1
        self.endDate = end_date_dt1
        start_date_fore = start_date_dt + relativedelta(days=dolu_veri)
        end_date_str = datetime.strftime(end_date_dt, "%Y-%m-%d")
        start_date_str = datetime.strftime(start_date_fore, "%Y-%m-%d")

        print("Tahmine Baslama Tarihi: ", start_date_str)
        print("Tahmini Bitirme Tarihi: ", end_date_str)
        for i in range(0, dolu_veri, 1):
            print("Days: ", i)
            # 10 gunluk veri egitilir
            if i < dolu_veri:
                request_data = requests.get(self.urls[i])
                print(request_data)
                if len(request_data.content) > 0:
                    data = json.loads(request_data.content)
                    for key, value in (data[0]['dps']).items():
                        self.learn_data = self.learn_data.append([[key, value]], True)
            if i == dolu_veri:
                print("Egitim Tamamlandi..")

        self.learn_data.index = pd.to_datetime(self.learn_data[0], unit="s")
        self.learn_data = self.learn_data.drop(0, axis=1)
        self.learn_data.columns = ["value"]
        self.learn_data = self.learn_data.iloc[1:]
        self.learn_data = pd.DataFrame(self.learn_data)
        print(self.learn_data)

    def outlier(self):
        print('outlier calisti')
        start_future = self.learn_data.head(1).index[0]
        print('startasdasdas:  ', start_future)
        start = datetime.strftime(start_future, "%Y/%m/%d")
        end = self.endDate
        print('start:  ', start)
        print('end:  ', end)
        print("anomali: ", self.anomali)
        q25, q75 = percentile(self.learn_data, 25), percentile(self.learn_data, 75)
        iqr = q75 - q25
        print('Percentiles: 25th=%.3f, 75th=%.3f, IQR=%.3f' % (q25, q75, iqr))
        # aykiri esik degerini hesapla
        cut_off = iqr * 1.2
        lower, upper = q25 - cut_off, q75 + cut_off

        # aykiri degerlerin belirlenmesi
        outliers = list()
        for x in range(0, len(self.learn_data), 1):
            data = self.learn_data.values[x]
            if data < lower or data > upper:
                outliers.append(x)
        def cut_indices(outliers):
            # this function iterate over the indices that need to be 'cut'
            for i in range(len(outliers) - 1):
                if outliers[i + 1] - outliers[i] > 1:
                    yield i + 1
        def splitter(outliers):
            # this function split the original list into sublists.
            px = 0
            for x in cut_indices(outliers):
                yield outliers[px:x]
                px = x
            yield outliers[px:]
        def cluster(outliers):
            # using the above result, to form a dict object.
            cluster_ids = range(1, len(outliers))
            return dict(zip(cluster_ids, splitter(outliers)))
        a = cluster(outliers)
        for a, b in a.items():
            bas = b[0]
            son = b[-1]
            aralik = (int(son) - int(bas) + 1)
            last = self.learn_data.iloc[son + 1, 0]
            first = self.learn_data.iloc[bas - 1, 0]
            deger = abs((last - first) / aralik)
            for i in range(0, aralik, 1):
                print("Anomali veriler: ", self.learn_data.iloc[bas + i, 0])
                if first < last:
                    self.learn_data.iloc[bas + i, 0] = self.learn_data.iloc[bas + i - 1, 0] + deger
                    print("Degisen veriler: ", self.learn_data.iloc[bas + i, 0])
                else:
                    self.learn_data.iloc[bas + i, 0] = self.learn_data.iloc[bas + i - 1, 0] - deger
                    print("Degisen veriler: ", self.learn_data.iloc[bas + i, 0])
    def date_liste(self):
        start_future = self.learn_data.tail(1).index[0]
        if self.zamanDilimi == 'm':
            self.step_sec = round(60 * 24 / int(self.textZaman) * int(self.step_size))
            self.date_list = [start_future + relativedelta(minutes=x) for x in
                         range(int(self.textZaman), self.step_sec * int(self.textZaman), int(self.textZaman))]
        # Saniye
        elif self.zamanDilimi == 's':
            self.step_sec = round(60 * 60 * 24 / int(self.textZaman) * int(self.step_size))
            self.date_list = [start_future + relativedelta(seconds=x) for x in
                         range(int(self.textZaman), self.step_sec * int(self.textZaman), int(self.textZaman))]
        # Saat
        elif self.zamanDilimi == 'h':
            self.step_sec = round(24 / int(self.textZaman) * int(self.step_size))
            self.date_list = [start_future + relativedelta(hours=x) for x in
                         range(int(self.textZaman), self.step_sec * int(self.textZaman), int(self.textZaman))]
        # Gun
        elif self.zamanDilimi == 'd':
            self.step_sec = round(1 / int(self.textZaman) * int(self.step_size))
            self.date_list = [start_future + relativedelta(days=x) for x in
                         range(int(self.textZaman), self.step_sec * int(self.textZaman), int(self.textZaman))]
        # Hafta
        elif self.zamanDilimi == 'w':
            self.step_sec = round(1 / 7 / int(self.textZaman) * int(self.step_size))
            self.date_list = [start_future + relativedelta(weeks=x) for x in
                         range(int(self.textZaman), self.step_sec * int(self.textZaman), int(self.textZaman))]
        # Ay
        elif self.zamanDilimi == 'n':
            self.step_sec = round(1 / 30 / int(self.textZaman) * int(self.step_size))
            self.date_list = [start_future + relativedelta(month=x) for x in
                         range(int(self.textZaman), self.step_sec * int(self.textZaman), int(self.textZaman))]
        # Yil
        elif self.zamanDilimi == 'y':
            self.step_sec = round(1 / 365 / int(self.textZaman) * int(self.step_size))
            self.date_list = [start_future + relativedelta(year=x) for x in
                         range(int(self.textZaman), self.step_sec * int(self.textZaman), int(self.textZaman))]
        print(self.startDate)
        print(self.endDate)
        print(self.step_size)

    def run(self):
        self.veri_al()
        self.duzenle()
        if self.anomali == '1':
            self.outlier()
        if self.analysisType == 'Sarima' or self.analysisType == 'LSTM':
            self.date_liste()
        if self.analysisType == 'Arima':
            ModelArima(self.learn_data, str(self.startDate), str(self.endDate)).run()
        elif self.analysisType == 'Sarima':
            ModelSarima(self.learn_data, str(self.startDate), str(self.endDate), self.date_list).run()
        elif  self.analysisType == 'LSTM':
            ModelLSTM(self.learn_data, str(self.startDate), str(self.endDate),self.step_sec).run()
        elif self.analysisType == 'Anomali':
            ModelOutlier(self.learn_data).run()

        return True