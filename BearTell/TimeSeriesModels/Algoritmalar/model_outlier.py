# -*- coding: utf-8 -*-
from matplotlib import pyplot
from numpy import percentile

class ModelOutlier(object):
    def __init__(self, learn_data):
        self.learn_data = learn_data
        self.url_len = len(learn_data)
    def run(self):
        q25, q75 = percentile(self.learn_data, 25), percentile(self.learn_data, 75)
        iqr = q75 - q25
        print('Percentiles: 25th=%.3f, 75th=%.3f, IQR=%.3f' % (q25, q75, iqr))
        # aykiri esik degerini hesapla
        cut_off = iqr * 1.5
        lower, upper = q25 - cut_off, q75 + cut_off
        # aykiri degerlerin belirlenmesi
        degisenler = list()
        for x in self.learn_data.values:
            if x < lower or x > upper:
                degisenler.append(x)
                print(x)
            else:
                degisenler.append(0)
        print('Bulunan outlier sayisi: %d' % len(degisenler))
        pyplot.plot(self.learn_data.values)
        pyplot.plot(degisenler,'ro')
        pyplot.savefig('outlier_')
        pyplot.show()