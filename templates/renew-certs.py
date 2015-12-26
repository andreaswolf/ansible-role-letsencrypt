#!/usr/bin/env python

from subprocess import Popen, PIPE, STDOUT

keys = {{ letsencrypt_keys }}

script = "{{ acme_tiny_software_directory }}/acme_tiny.py"

for cert in keys:
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
