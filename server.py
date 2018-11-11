import argparse
import heapq
import pickle
import socket
import time
import uuid


class TaskQueueServer:
    def __init__(self, ip, port, path, timeout):
        self.ip = ip
        self.port = port
        self.path = path
        self.timeout = timeout
        self.contain = Contain()

    def ack_action(self, data, connect):
        if self.contain.ack_task(data):
            connect.send(b'YES')
        else:
            connect.send(b'NO')

    def add_action(self, data, connect):
        id = str(self.unique_id())
        self.contain.add_task(data, id)
        connect.send(bytes(id, 'utf-8'))

    def get_action(self, data, connect):
        task = self.contain.get_task(data, self.timeout)
        if task:
            connect.send(bytes("{} {} {}".format(task[1], task[2], task[3]), 'utf-8'))
        else:
            connect.send(b'NONE')

    def in_action(self, data, connect):
        if self.contain.in_heap(data):
            connect.send(b'YES')
        else:
            connect.send(b'NO')

    def parse(self, connect):
        connect.setblocking(0)
        temp = b''
        while 1:
            try:
                temp += connect.recv(128)
            except BlockingIOError:
                break
        data = temp.decode("utf-8")
        data = data.split()
        self.contain.update()
        self.work_with_req(data, connect)

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(10)
        while True:
            try:
                connect, addr = self.sock.accept()
                self.parse(connect)
                connect.close()
            except KeyboardInterrupt:
                self.sock.close()
                break

    def save(self, connect):
        self.contain.save(self.path)
        connect.send(b'OK')

    def unique_id(self):
        return uuid.uuid1()

    def work_with_req(self, data, connect):
        if data[0] == "ADD":
            if not int(data[2]) > 1000000 and len(data[3]) == int(data[2]):
                self.add_action(data, connect)
            else:
                connect.send(b'ERROR')
        elif data[0] == "GET":
            self.get_action(data, connect)
        elif data[0] == "ACK":
            self.ack_action(data, connect)
        elif data[0] == "IN":
            self.in_action(data, connect)
        elif data[0] == "SAVE":
            self.save(connect)
        else:
            connect.send(b'ERROR')
        return


class Contain():
    def __init__(self):
        self.heap, self.buff_heap = self.load('heap')

    def ack_task(self, data):
        task = self.search_task(data, self.buff_heap)
        if task:
            self.buff_heap[data[1]].remove(task)
            return True
        return False

    def add_task(self, data, unique_id):
        if data[1] not in self.heap:
            self.heap[data[1]] = []
        heapq.heappush(self.heap[data[1]], [self.gen_time(), unique_id, data[2], data[3]])

    def gen_time(self):
        return time.time()

    def get_task(self, data, timeout):
        if data[1] not in self.heap or len(self.heap[data[1]]) == 0:
            return False
        else:
            task = heapq.heappop(self.heap[data[1]])
            task.append(self.gen_time() + float(timeout))
            if data[1] not in self.buff_heap.keys():
                self.buff_heap[data[1]] = []
            heapq.heappush(self.buff_heap[data[1]], task)
            return task

    def in_heap(self, data):
        if self.search_task(data, self.heap) or self.search_task(data, self.buff_heap):
            return True
        return False

    def load(self, name):
        heap = ({}, {})
        try:
            f = open((path + 'heap'), 'wb')
            heap = pickle.load(f)
            f.close()
        except IOError:
            raise IOError
        except PermissionError:
            raise PermissionEror
        finally:
            return heap

    def save(self, path):
        f = open((path + 'heap'), 'wb')
        pickle.dump((self.heap, self.buff_heap), f)
        f.close()

    def search_task(self, data, heap):
        if data[1] in heap.keys():
            for task in heap.get(data[1]):
                if data[2] in task:
                    return task
        return False

    def update(self):
        for que, tasks in self.buff_heap.items():
            if tasks != None:
                for task in tasks:
                    if time.time() > float(task[4]):
                        heapq.heappush(self.heap[que], task[:-1])
                        self.buff_heap[que].remove(task)
                    else:
                        break


def parse_args():
    parser = argparse.ArgumentParser(description='This is a simple task queue server with custom protocol')
    parser.add_argument(
        '-p',
        action="store",
        dest="port",
        type=int,
        default=5555,
        help='Server port')
    parser.add_argument(
        '-i',
        action="store",
        dest="ip",
        type=str,
        default='0.0.0.0',
        help='Server ip adress')
    parser.add_argument(
        '-c',
        action="store",
        dest="path",
        type=str,
        default='./',
        help='Server checkpoints dir')
    parser.add_argument(
        '-t',
        action="store",
        dest="timeout",
        type=int,
        default=4,
        help='Task maximum GET timeout in seconds')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    server = TaskQueueServer(**args.__dict__)
    server.run()
