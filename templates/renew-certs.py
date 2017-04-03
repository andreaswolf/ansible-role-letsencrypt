#!/usr/bin/env python
import os
import pwd
import time
from subprocess import Popen, PIPE

def main():
    """Main entry-point for certificate renewal"""
    renewed = run_renew()
    if renewed:
        run_post_renew_cmd()

def run_renew():
    """Renews the certificate (run as the letsencrypt user)"""
    certs = {{letsencrypt_certs}}
    script = '{{ acme_tiny_software_directory }}/acme_tiny.py'
    renewed = False

    user_name = '{{ letsencrypt_user }}'
    pw_record = pwd.getpwnam(user_name)
    user_name = pw_record.pw_name
    user_uid = pw_record.pw_uid
    user_gid = pw_record.pw_gid
    env = os.environ.copy()
    env['USER'] = user_name

    for cert in certs:
        if os.access(cert['certpath'], os.F_OK):
            stat = os.stat(cert['certpath'])
            print 'Certificate file ' + cert['certpath'] + ' already exists'

            if time.time() - stat.st_mtime < {{ letsencrypt_min_renewal_age }} * 86400:
                print ('  The certificate is younger than {{ letsencrypt_min_renewal_age }} days.' +
                       ' Not creating a new certificate.\n')
                continue

        host = ','.join(cert['host']) if type(cert['host']) is list else cert['host']

        print 'Generating certificate for ' + host
        args = [
            '/usr/bin/env', 'python', script,
            '--account-key',
            '{{ letsencrypt_account_key }}',
            '--csr',
            '{{ acme_tiny_data_directory }}/csrs/' + cert['name'] + '.csr',
            '--acme-dir',
            '{{ acme_tiny_challenges_directory }}'
        ]

        cmd = ' '.join(args)
        p = Popen(
            cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True,
            preexec_fn=demote(user_uid, user_gid), env=env
        )
        output = p.stdout.read()
        p.stdin.close()
        if p.wait() != 0:
            print 'error while generating certificate for {}'.format(host)
            print p.stderr.read()
        else:
            f = open(cert['certpath'], 'w')
            f.write(output)
            f.close()
            renewed = True

    return renewed


def run_post_renew_cmd():
    """Optionally runs a command after renewal (run as the root user)"""
    post_renew_cmd = '{{ letsencrypt_post_renew_cmd }}'
    if not len(post_renew_cmd):
        print 'No post-renew command configured'
        return

    process = Popen(
        post_renew_cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True
    )
    output = process.stdout.read()
    process.stdin.close()
    if process.wait() != 0:
        print 'Error while running post-renew command: {}'.format(post_renew_cmd)
        print process.stderr.read()
    else:
        print 'Post-renew command completed successfully'


def demote(user_uid, user_gid):
    """Demotes to a non-root user before running a command"""
    def result():
        os.setgid(user_gid)
        os.setuid(user_uid)
    return result


if __name__ == '__main__':
    main()
