import shutil
import sys
import tempfile
import datetime
import time
import subprocess
import logging
from pprint import pformat


def checked_key_scan(host):
    scan_args = ['/usr/bin/ssh-keyscan', '-t', 'rsa', host]
    count = 5
    output = subprocess.check_output(scan_args, stderr=None).strip()
    logging.info("Executed keyscan with args=" + pformat(scan_args) + " and got output=" + output)
    while len(output) == 0 and count > 0:
        logging.error("Got back empty value from SSH keyscan, retrying")
        count -= 1
        time.sleep(5)
        output = subprocess.check_output(scan_args, stderr=None).strip()

    if len(output) == 0:
        raise IOError("empty results from ssh-keyscan")

    # Test
    # output = host + "  ssh-rsa 1111111111111111111111\n"
    return output

def update_knownhosts_file(host):
    orig_file = '~/.ssh/known_hosts'
    bak_file = orig_file + '.bak'
    host_exist = False
    temp = tempfile.NamedTemporaryFile(delete=False)
    print 'temp ' + temp.name

    with open(orig_file, 'r') as f1:
        for line in f1:
            print line
            if line.startswith('#'):
                temp.write("# import_new_ssh_keys on " + str(datetime.datetime.now()) + " for host " + host + '\n')
            else:
                words = line.split()
                if len(words) == 3:
                    if host == words[0]:
                        host_exist = True
                        temp.write(checked_key_scan(host))
                    else:
                        temp.write(line)
                else:
                    print 'Bad line format, ignoring: ' + line

    if not host_exist:
        temp.write(checked_key_scan(host))
        host_exist = True

    if host_exist:
        shutil.copyfile(orig_file, bak_file)
        shutil.move(temp.name, orig_file)

update_knownhosts_file(sys.argv[1])
