# -*- coding: utf-8 -*-

from flask import Flask, request
from ModelRunner import ModelRunner
import _thread
import queue

work_que = queue.Queue()
app = Flask(__name__)

def work_runner():
    while True:
        work = work_que.get()
        model = ModelRunner(work)
        model.run()
def flaskThread():
    app.run()

@app.route("/v1/", methods=['GET'])
def api_model_runner():
    work_que.put(request.args)
    return "200"

if __name__ == "__main__":
    _thread.start_new_thread(work_runner, ())
    _thread.start_new_thread(flaskThread, ())

    while 1:
        pass


