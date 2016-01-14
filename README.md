# Let’s encrypt/acme-tiny role for Ansible

Installs and configures [acme-tiny](https://github.com/debops/acme-tiny), a small Python-based client for
[Let’s encrypt](https://letsencrypt.org).

It automates the following tasks:

  * creating an account key for Let’s encrypt
  * creating private keys and Certificate Signature Requests (CSR) for hosts
  * configuring a cron job that automatically renews the certificates at the beginning of each month

Currently, you need to run the cron job manually to get a new certificate after running Ansible. This shortcoming will
be fixed.


## Requirements

For every hostname you want to support, you need to have a webserver configured and add an alias that points to the 
directory configured with `acme_tiny_challenges_directory`. For Apache, such an alias should look like this:

    Alias "/.well-known/acme-challenge" "{{ acme_tiny_challenges_directory }}"


## Role Variables

You might want to adjust these variables that control where the software and data are located:

  * `acme_tiny_software_directory`: The location to which acme-tiny is cloned
  * `acme_tiny_data_directory`: The location where the account key and certificate signature requests (CSR) are placed
  * `acme_tiny_challenges_directory`: The (web-reachable) directory that contains the temporary challenges used for 
    verifying your domain ownership

You can also adjust the user and group used for generating the certificates; there should be a dedicated user for this
(recommended by the acme-tiny authors). The user and group are configured with these two variables:

  * `letsencrypt_user`—note that this is a user **on your system**, not with the Let’s encrypt web service.
  * `letsencrypt_group`

Add the certificates to generate to their respective hosts:

    letsencrypt_certs:
      - 
        name: "an_easily_recognizable_name__this_is_used_for_the_csr_file"
        keypath: "/path/to/your/keys/anything-you-like.key"
        certpath: "/path/to/your/certs/anything-you-like.cert"
        host: "myhost.example.com"
      -
        name: "multidomain cert"
        keypath: "/path/to/your/keys/example.org.key"
        certpath: "/path/to/your/certs/example.org.cert"
        host:
          - "foo.example.org"
          - "bar.example.org"

For multidomain certificates, all mentioned names must point to the server where the certificate is being generated.

You can optionally also set the permissions of the key, with these three options which are fed in to Ansible’s file
module:

  - key_owner: a user name, e.g. root or www-data
  - key_group: a group name, e.g. root or ssl-certs or www-data
  - key_permissions: an octal mode, like "0600". This must be specified as a quoted string. Without the quotes, it did
    not work for me (read: the number was interpreted as octal and converted to decimal)

The default mode is root/root/0600, i.e. the file is only read-/writable by root. Make sure you never make the key
world-readable! If you do, everybody with shell access to the server might be able to compromise your encrypted
connections.


## Dependencies

No direct dependencies, but of course you will need to have a webserver configured (e.g. Apache); this role currently
does not support setting up a temporary server.


## Example Playbook

    - hosts: servers
      roles:
         - role: andreaswolf.letsencrypt
      
      vars:
        letsencrypt_certs:
          -
            name: "think_of_something_unique_or_nice_here" # :-)
            keypath: "/etc/ssl/private/anything-you-like.key"
            certpath: "/etc/ssl/certs/anything-you-like.cert"
            host: "myhost.example.com"

## TODO

This role is brand-new, so it needs testing. I tested it on Debian, where it works fine, but YMMV. If you can get it to
run on other systems, I’d be happy to hear about that. I’m also happy if you report any issues you run into.

During its public beta, _Let’s encrypt_ has a rate-limit of five certificates *per domain* per seven days 
[source](https://community.letsencrypt.org/t/public-beta-rate-limits/4772). So two certificates for foo.example.org
and bar.example.org use two of the seven available certs for example.org. This should be better handled by the role,
by not regenerating certficates too often (probably you have multiple servers which host subdomains of the same domain,
so the limit would be depleted very fast).

Also the private keys are currently not limited to a certain user; this would require some more logic that will follow
soon.


## License

MIT


## Author Information

This role was created by Andreas Wolf. Visit my [website](http://a-w.io) and 
[Github profile](https://github.com/andreaswolf/) or follow me on [Twitter](https://twitter.com/andreaswo).

### Contributors

*(in alphabetic order)*

  * [tgagor](https://github.com/tgagor)
  * [Ludovic Claude](https://github.com/ludovicc)
