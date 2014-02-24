#!/usr/bin/env python

import argh
import time
import threading
from novaclient.v1_1 import client as nova_client

lock = threading.RLock()

class BootThread(threading.Thread):
    def __init__(self, nova, name, image_id, flavor_id, networks):
        super(BootThread, self).__init__()
        self.nova = nova
        self.name = name
        self.image_id = image_id
        self.flavor_id = flavor_id
        self.networks = networks

    def run(self):
        with lock:
            print "{name} booting".format(name=self.name)
        try:
            ret = self.nova.servers.create(self.name, self.image_id,
                                           self.flavor_id, nics=self.networks)
        except Exception as e:
            with lock:
                print "{name} error:{err}".format(name=self.name, err=e)
            return

        server = self.wait_for_state(self.nova.servers.get, ret,
                                     "status", ["ACTIVE", "ERROR"])
        with lock:
            print "{name} complete".format(name=self.name)

    def wait_for_state(self, fun, obj, attr, desired, interval=.1,
                       attempts=None):
        attempt = 0
        in_attempt = lambda x: not attempts or attempts > x
        while getattr(obj, attr) not in desired and in_attempt(attempt):
            time.sleep(interval)
            obj = fun(obj.id)
            attempt = attempt + 1
        return obj

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '%s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
        return ret
    return wrap

@timing
def build(nova, cycles, interval, count, step, image_id, flavor_id, networks):
    for cycle in xrange(cycles):
        for tcount in xrange(count):
            name = "{cycle}-{count}".format(cycle=cycle, count=tcount)
            thread = BootThread(nova, name, image_id, flavor_id, networks)
            thread.start()
            threads.append(thread)
        count = count + int(step)
        time.sleep(int(interval))

    for thread in threads:
        thread.join(timeout=10)

def main(user, key, tenant, url, duration, interval, count, step=0):
    nova = nova_client.Client(user, key, tenant, auth_url=url, insecure=True)
    image_id = next(i for i in nova.images.list() if "cirros" in i.name)
    flavor_id = next(i for i in nova.flavors.list() if "tiny" in i.name)
    networks=[{"net-id": i.id} for i in nova.networks.list()]
    cycles = int(duration)/int(interval)
    count = int(count)
    threads = []

    print "{0} cycles".format(cycles)

    build(nova, cycles, interval, count, step, image_id, flavor_id, networks)

argh.dispatch_command(main)
