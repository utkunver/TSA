# -*- coding: utf-8 -*-
from pandas import DataFrame
from pandas import concat
from matplotlib import pyplot
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
import numpy
from sklearn.preprocessing import MinMaxScaler
from pandas import Series

class ModelLSTM(object):
    def __init__(self, learn_data, start, end, step_sec):
        self.learn_data = learn_data
        self.start = start
        self.end = end
        self.step_sec = step_sec

    def run(self):
        # frame a sequence as a supervised learning problem
        def timeseries_to_supervised(data, lag=1):
            df = DataFrame(data)
            columns = [df.shift(i) for i in range(1, lag + 1)]
            columns.append(df)
            df = concat(columns, axis=1)
            df.fillna(0, inplace=True)
            return df

        # create a differenced series
        def difference(dataset, interval=1):
            diff = list()
            for i in range(interval, len(dataset)):
                value = dataset[i] - dataset[i - interval]
                diff.append(value)
            return Series(diff)

        # invert differenced value
        def inverse_difference(history, yhat, interval=1):
            return yhat + history[-interval]

        # scale train and test data to [-1, 1]
        def scale(train, test):
            # fit scaler
            scaler = MinMaxScaler(feature_range=(-1, 1))
            scaler = scaler.fit(train)
            # transform train
            train = train.reshape(train.shape[0], train.shape[1])
            train_scaled = scaler.transform(train)
            # transform test
            test = test.reshape(test.shape[0], test.shape[1])
            test_scaled = scaler.transform(test)
            return scaler, train_scaled, test_scaled

        # inverse scaling for a forecasted value
        def invert_scale(scaler, X, value):
            new_row = [x for x in X] + [value]
            array = numpy.array(new_row)
            array = array.reshape(1, len(array))
            inverted = scaler.inverse_transform(array)
            return inverted[0, -1]

        # fit an LSTM network to training data
        def fit_lstm(train, batch_size, nb_epoch, neurons, epoch):
            X, y = train[:, 0:-1], train[:, -1]
            X = X.reshape(X.shape[0], 1, X.shape[1])
            model = Sequential()
            model.add(LSTM(neurons, batch_input_shape=(batch_size, X.shape[1], X.shape[2]), stateful=True))
            model.add(Dense(1))
            model.compile(loss='mean_squared_error', optimizer='adam')
            for i in range(nb_epoch):
                model.fit(X, y, epochs=epoch, batch_size=batch_size, verbose=2, shuffle=False)
                model.reset_states()
            return model

        # make a one-step forecast
        def forecast_lstm(model, batch_size, X):
            X = X.reshape(1, 1, len(X))
            yhat = model.predict(X, batch_size=batch_size)
            return yhat[0, 0]

        # transform data to be stationary
        raw_values = self.learn_data.values
        diff_values = difference(raw_values, 1)
        start_future = self.learn_data.tail(1).index[0]
        _epoc = 10
        _neuron = 1
        _nb_epoch = 1
        # transform data to be supervised learning
        supervised = timeseries_to_supervised(diff_values, 1)
        supervised_values = supervised.values
        trainn = (len(supervised_values) * 0.6)
        testt = (len(supervised_values) - int(trainn) + 1)
        # split data into train and test-sets
        train, test = supervised_values[0:int(trainn), :], supervised_values[int(trainn):len(supervised_values), :]
        # transform the scale of the data
        scaler, train_scaled, test_scaled = scale(train, test)
        # fit the model
        lstm_model = fit_lstm(train_scaled, 1, _nb_epoch, _neuron, _epoc)
        # forecast the entire training dataset to build up state for forecasting
        train_reshaped = train_scaled[:, 0].reshape(len(train_scaled), 1, 1)
        lstm_model.predict(train_reshaped, batch_size=1)
        # walk-forward validation on the test data
        predictions = list()
        for i in range(len(test_scaled)):
            # make one-step forecast
            X, y = test_scaled[i, 0:-1], test_scaled[i, -1]
            yhat = forecast_lstm(lstm_model, 1, X)
            # invert scaling
            yhat = invert_scale(scaler, X, yhat)
            # invert differencing
            yhat = inverse_difference(raw_values, yhat, len(test_scaled) + 1 - i)
            # store forecast
            predictions.append(yhat)
            expected = raw_values[len(train) + i + 1]

        last_data = test_scaled
        calculated_step_count = int(self.step_sec)
        total_range = calculated_step_count + len(last_data)
        for	i in range(len(last_data)-1,total_range,1):
            X, y = last_data[i,0:1], last_data[i, 1:2]
            yhat = forecast_lstm(lstm_model, 1, X)
            new_rows = numpy.append(y, yhat)
            last_data= numpy.vstack((last_data,new_rows))
            yhat = invert_scale(scaler, X, yhat)
            yhat = inverse_difference(raw_values, yhat, len(test_scaled)+1-i)
            predictions.append(yhat)
        for i in range(len(train_scaled)):
         predictions.insert(0, 0)
        pyplot.figure(figsize=(10,8))
        pyplot.plot(predictions,  c='g' ,label="Forecast")
        pyplot.plot(raw_values, c='b' , label="Test Data" )
        pyplot.legend()
        pyplot.show()
        pyplot.savefig('lstm_')
