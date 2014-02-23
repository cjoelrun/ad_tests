#!/usr/bin/env python

import argh
import threading
from time import sleep
from novaclient.v1_1 import client as nova_client


class BootThread(threading.Thread):
    def __init__(self, nova, name, image_id, flavor_id, networks):
        super(BootThread, self).__init__()
        self.nova = nova
        self.name = name
        self.image_id = image_id
        self.flavor_id = flavor_id
        self.networks = networks

    def run(self):
        self.nova.servers.create(self.name, self.image_id,
                                 self.flavor_id, nics=self.networks)

def main(user, key, tenant, url, duration, interval, count, step=0):
    nova = nova_client.Client(user, key, tenant, auth_url=url)
    image_id = next(i for i in nova.images.list() if "cirros" in i.name)
    flavor_id = next(i for i in nova.flavors.list() if "tiny" in i.name)
    networks=[{"net-id": i.id} for i in nova.networks.list()]
    cycles = int(duration)/int(interval)
    threads = []

    for cycle in xrange(int(cycles)):
        for count in xrange(int(count)):
            name = "{cycle}-{count}".format(cycle=cycle, count=count)
            thread = BootThread(nova, name, image_id, flavor_id, networks)
            thread.start()
            threads.append(thread)
        count = int(count) + int(step)
        sleep(int(interval))

    for thread in threads:
        thread.join(timeout=10)

argh.dispatch_command(main)
