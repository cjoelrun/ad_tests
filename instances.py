#!/usr/bin/env python

import argh
import threading
from novaclient.v1_1 import client as nova_client


class BootThread(threading.Thread):
    def __init__(self, name, image_id, flavor_id, networks):
        self.name = name
        self.image_id = image_id
        self.flavor = flavor_id
        self.networks = networks

    def run(self):
        self.compute_client.servers.create(self.name, self.image_id,
                                           self.flavor_id, nics=self.networks)

def main(user, key, tenant, url, duration, interval, count, step=0):
    nova = nova_client.Client(user, key, tenant, auth_url=url)
    cycles = duration/interval
    threads = []

    for cycle in xrange(cycles):
        for count in xrange(count):
            name = "{cycle}-{count}".format(cycle=cycle, count=count)
            thread = BootThread(name, image_id, flavor_id, networks)
            thread.start()
            threads.append(thread)
        count = count + step
        sleep(interval)

    for thread in threads:
        thread.join(timeout=10)

argh.dispatch_command(main)
