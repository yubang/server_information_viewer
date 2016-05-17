# coding:UTF-8

import tornado.web
import tornado.ioloop
import config
import psutil
import json
import time
import thread


settings = {
    'debug': True
}


cpu_data = 100
memory_data = [0, 0]
process_nums = 0
disk_datas = []


def flush_cpu():
    global cpu_data
    r = psutil.cpu_percent(1, True)
    cpu_data = sum(r) / len(r)


def flush_memory():
    global memory_data
    r = psutil.virtual_memory()
    memory_data[0] = r.percent
    r = psutil.swap_memory()
    memory_data[1] = r.percent


def flush_disks():
    global disk_datas
    del disk_datas[:]
    r = psutil.disk_partitions()
    for obj in r:
        d = psutil.disk_usage(obj.mountpoint)
        disk_datas.append({
            'total': d.total,
            'used': d.used,
            'free': d.free,
            'percent': d.percent,
            'mountpoint': obj.mountpoint
        })


def flush_messages():
    flush_cpu()
    print cpu_data
    flush_memory()
    print memory_data
    flush_disks()
    print disk_datas


def init():
    while True:
        try:
            flush_messages()
        except:
            pass
        time.sleep(5)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('ok')

    def post(self):

        if self.get_body_argument('token', None) != config.token:
            self.write({})
            return None

        global cpu_data, memory_data, disk_datas
        self.set_header("Content-Type", "application/json")
        d = json.dumps({
            'cpu': cpu_data,
            'memory': memory_data,
            'disks': disk_datas
        })
        self.write(d)

routes = [
    (r'/data', IndexHandler),
]

app = tornado.web.Application(routes, **settings)

if __name__ == '__main__':
    thread.start_new_thread(init, tuple())
    app.listen(config.port, config.host)
    tornado.ioloop.IOLoop.instance().start()
