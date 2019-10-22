# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from statsmodels.tsa.arima_model import ARMA,ARIMA


class ModelArima:
    def __init__(self, learn_data, start, end):
        self.learn_data = learn_data
        self.start = start
        self.end = end

    def run(self):
        # Arma modeli baslangic
        model_result = {}
        model_parameters = {}

        # Ar(1)
        mod = ARMA(self.learn_data, order=(1, 0))
        res = mod.fit()
        model_result[0] = res.aic
        model_parameters[0] = (1, 0)

        # Ar(2)
        mod = ARMA(self.learn_data, order=(2, 0))
        res = mod.fit()
        model_result[1] = res.aic
        model_parameters[1] = (2, 0)

        # Ma(1)
        mod = ARMA(self.learn_data, order=(0, 1))
        res = mod.fit()
        model_result[2] = res.aic
        model_parameters[2] = (0, 1)

        # Arma(1,1)
        mod = ARMA(self.learn_data, order=(1, 1))
        res = mod.fit()
        model_result[3] = res.aic
        model_parameters[3] = (1, 1)

        less_value_index = 0
        for index, value in model_result.items():
            if less_value_index == 0:
                less_value_index = index
            elif value < less_value_index:
                less_value_index = index

        # Arma Model Btis
        print('-------------')
        # Algoritmalar modeli forecast cizimi
        mod = ARIMA(self.learn_data, order=(model_parameters[less_value_index][0], 1, model_parameters[less_value_index][1]))
        res = mod.fit()
        res.plot_predict(start=self.start, end=self.end)
        plt.show()
        plt.savefig('arima_')
