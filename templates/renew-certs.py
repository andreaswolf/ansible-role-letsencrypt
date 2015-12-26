#!/usr/bin/env python

import os
import time

from subprocess import Popen, PIPE, STDOUT

certs = {{letsencrypt_certs}}

script = "{{ acme_tiny_software_directory }}/acme_tiny.py"

for cert in certs:
    if os.access(cert['certpath'], os.F_OK):
        stat = os.stat(cert['certpath'])
        if time.time() - stat.st_mtime < 14 * 86400:
            print "Certificate file " + cert['certpath'] \
                  + " already exists and is younger than 14 days. Not creating a new certificate.\n"
            continue

    print "Generating certificate for " + cert["host"]
    args = [
        "/usr/bin/env", "python", script,

        "--account-key",
        "{{ letsencrypt_account_key }}",
        "--csr",
        "{{ acme_tiny_data_directory }}/csrs/" + cert['name'] + ".csr",
        "--acme-dir",
        "{{ acme_tiny_challenges_directory }}"
    ]

    cmd = "/usr/bin/env " + " ".join(args)

    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    output = p.stdout.read()
    p.stdin.close()
    if p.wait() != 0:
        print "error while generating certificate for " + cert['host']
        print p.stderr.read()
    else:
        f = open(cert['certpath'], 'w')
        f.write(output)
        f.close()
