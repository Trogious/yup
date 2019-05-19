#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from threading import Thread, Lock

YUP_stderr_lock = Lock()
YUP_stderr = sys.stderr


class Uploader(Thread):
    def __init__(self, cfg, entries):
        Thread.__init__(self)
        self.cfg = cfg
        self.entries = entries

    def escape(self, entry):
        return entry

    def get_title(self, entry):
        return os.path.basename(entry).replace('.mp4', '').replace('.', ' ')

    def run(self):
        # self.cfg['command'] = '/root/workspace/yup/dummy.py'
        for entry in self.entries:
            entry = self.escape(entry)
            if len(self.cfg['playlist'].strip()) > 0:
                cmd = [self.cfg['command'], '--client-secrets=' + self.cfg['secrets'], '--credentials-file=' + self.cfg['credentials'], '--category=' + self.cfg['category'], '--playlist=' + self.cfg['playlist'], '--title=' + self.get_title(entry), entry]
            else:
                cmd = [self.cfg['command'], '--client-secrets=' + self.cfg['secrets'], '--credentials-file=' + self.cfg['credentials'], '--category=' + self.cfg['category'], '--title=' + self.get_title(entry), entry]
            try:
                subprocess.run(cmd)
                # RDLEN = 5
                # with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
                #     data = p.stdout.read(RDLEN)
                #     while len(data) > 0:
                #         txt = data.decode('utf8')
                #         idx = txt.find('%')
                #         import re
                #         if idx > 0:
                #             m = re.match('\d+', txt)
                #             if m is not None:
                #                 print(m.group())
                #
                #         data = p.stdout.read(RDLEN)
                os.remove(entry)
            except Exception as e:
                log(e)


def log(log_item):
    with YUP_stderr_lock:
        YUP_stderr.write(str(log_item) + '\n')
        YUP_stderr.flush()


def upload(cfg):
    if 'path' in cfg.keys():
        path = cfg['path']
        if len(path) > 0 and os.path.isdir(path):
            uploaders = []
            for root, dirs, files in os.walk(path):
                for f in files:
                    if f.endswith('.mp4'):
                        u = Uploader(cfg, [os.path.join(root, f)])
                        uploaders.append(u)
                        # u.start()
                        u.run()
            for u in uploaders:
                pass  # u.join()


def usage():
    log('Usage: ' + sys.argv[0] + ' <config_file>\n\nArguments:\n config_file - JSON file containing configuration parameters\n\nOptions:\n --generate-config - generates config file skeleton\n')


def generate_config():
    cfg = {'command': '', 'secrets': '', 'credentials': '', 'category': '', 'playlist': '', 'path': ''}
    try:
        with open('config.json', 'w') as f:
            f.write(json.dumps(cfg, indent=4))
    except Exception as e:
        log(e)


def main():
    a_len = len(sys.argv)
    if a_len < 2:
        usage()
    elif '--generate-config' in sys.argv[1]:
        generate_config()
    elif sys.argv[1].endswith('.json') and os.path.isfile(sys.argv[1]):
        try:
            with open(sys.argv[1], 'r') as f:
                cfg = json.loads(f.read())
            upload(cfg)
        except Exception as e:
            log(e)
    else:
        usage()


if __name__ == '__main__':
    main()
