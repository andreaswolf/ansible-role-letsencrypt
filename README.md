# Let’s encrypt/acme-tiny role for Ansible

Installs and configures [acme-tiny](https://github.com/diafygi/acme-tiny), a small Python-based client for
[Let’s encrypt](https://letsencrypt.org).

It automates the following tasks:

  * creating an account key for Let’s encrypt
  * creating private keys and Certificate Signature Requests (CSR) for hosts
  * configuring a cron job that automatically renews the certificates after 60 days

During each role run, the certificate renewal script is also executed (as with the cron job), to ensure you get new
certificates as soon as you have configured them.


## Requirements

For every hostname you want to support, you need to have a webserver configured and add an alias that points to the 
directory configured with `acme_tiny_challenges_directory`. For Apache, such an alias should look like this:

    Alias "/.well-known/acme-challenge" "{{ acme_tiny_challenges_directory }}"

Hint: You can also put this into a global variable and then use this variable in the definition of every vHost.


## Certificate chain

The intermediate certificate of Let’s encrypt is downloaded to `letsencrypt_intermediate_cert_path`. You should include
it in the webserver config to have it delivered to visitors.

## Reusing existing account keys

When you use Letencrypt on multiple servers, it may be simpler to have only one account defined with Letsencypt. You can do that with this role by proceeding as follow:

1. Run the role on a first server, a new account.key file is created for you.
2. Register the account public key with Letsencrypt using for example [Gethttpsforfree](https://gethttpsforfree.com/)
3. Copy /var/lib/letsencrypt/account.key from the first server to your computer
4. Recommanded: secure the account.key file. It should never be accessible to anybody otherwise the security of your site may be compromised as an attacker may impersonate you. Personally, I use git-crypt with PGP encryption to protect this file.
5. For new servers, setup `letsencrypt_account_key_source` to point to the local account.key file. The file account.key will be copied to the server and you will be able to reuse the same account with Letencrypt for all your servers.

## Role Variables

You might want to adjust these variables that control where the software and data are located:

  * `acme_tiny_software_directory`: The location to which acme-tiny is cloned
  * `acme_tiny_data_directory`: The location where the account key and certificate signature requests (CSR) are placed
  * `acme_tiny_challenges_directory`: The (web-reachable) directory that contains the temporary challenges used for 
    verifying your domain ownership
  * `letsencrypt_intermediate_cert_path`: the path to which the intermediate certificate of Let’s encrypt will be
    downloaded.
  * `letsencrypt_account_key_source_file`: the path to the local account key file to copy over to the server. Leave this variable undefined to let this role generate the account key.
  * `letsencrypt_account_key_source_contents`: the actual content of the key file including the BEGIN and END headers. Leave this variable undefined to let this role generate the account key.

You can also adjust the user and group used for generating the certificates; there should be a dedicated user for this
(recommended by the acme-tiny authors). The user and group are configured with these two variables:

  * `letsencrypt_user`—note that this is a user **on your system**, not with the Let’s encrypt web service.
  * `letsencrypt_group`

Add the certificates to generate to their respective hosts (important! if the certificate is not generated on the host
the DNS A record points to, Let’s encrypt won’t be able to verify if the hostname really belongs to you and thus won’t
give you the certificate!):

    letsencrypt_certs:
      - 
        name: "an_easily_recognizable_name__this_is_used_for_the_csr_file"
        keypath: "/path/to/your/keys/anything-you-like.key"
        certpath: "/path/to/your/certs/anything-you-like.crt"
        chainedcertpath: "/path/to/your/certs/anything-you-like.chained.pem"
        host: "myhost.example.com"
      -
        name: "multidomain cert"
        keypath: "/path/to/your/keys/example.org.key"
        certpath: "/path/to/your/certs/example.org.crt"
        host:
          - "foo.example.org"
          - "bar.example.org"

The certificate will be placed in the path given in the `certpath` attribute.
The `chainedcertpath` option gives you a certificate file consisting of the actual certificate and the intermediate
certificate. This is e.g. useful for nginx. There is also a `fullchainedcertpath` option that works much the same, but
will include the private key in the output. Note that you always need to also have the `certpath` option set, even
if you only want to use the chained certificate.

For multidomain certificates, all mentioned names must point to the server where the certificate is being generated.

You can optionally also set the permissions of the key, with these three options which are fed in to Ansible’s file
module:

  - key_owner: a user name, e.g. root or www-data
  - key_group: a group name, e.g. root or ssl-certs or www-data
  - key_permissions: an octal mode, like "0600". This must be specified as a quoted string. Without the quotes, it did
    not work for me (read: the number was interpreted as octal and converted to decimal)

The default mode is root/root/0600, i.e. the file is only read-/writable by root. Make sure you never make the key
world-readable! If you do, everybody with shell access to the server might be able to compromise your encrypted
connections. You can also change the defaults by setting these variables:

  - letsencrypt_default_key_owner
  - letsencrypt_default_key_group
  - letsencrypt_default_key_permissions


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

Also desirable would be more ways to verify domain ownership than configuring a virtual host. I know there are others,
e.g. via DNS, but I did not look into them and they might require complicated setup. Also acme-tiny likely does not
support them currently, but that could be changed—it’s all open source here :-) So if you know your way around the ACME
protocol and/or other parts of the Let’s encrypt universe, feel free to contact me to work together on this.


## License

MIT


## Author Information

This role was created by Andreas Wolf. Visit my [website](http://a-w.io) and 
[Github profile](https://github.com/andreaswolf/) or follow me on [Twitter](https://twitter.com/andreaswo).

### Contributors

*(in alphabetic order)*

  * [Ludovic Claude](https://github.com/ludovicc)
  * [tgagor](https://github.com/tgagor)
