#!/usr/bin/env python

import os

keys = {{letsencrypt_keys}}

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

    result = os.execv("/usr/bin/env", args)

    print result
