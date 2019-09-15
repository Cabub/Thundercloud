# Thundercloud

## Immediate Goals

- Automatic encryption for data-at-rest
- Modular encryption methods so we can easily improve data security going forward
- REST API
- Collect/Store/Transfer as little data as possible

## Future Goals

- Client-side file encryption
- As close to zero knowledge as possible
 - Use hashes instead of usernames
 - No emails

 ## Encryption Model

When a user is created, we (will) create a backup key and a passphrase key
that will encrypt their (secret) session key.

backup keys and passphrase keys are derived using the passphrases provided,
then we use those to decrypt the session key.

Files are encrypted individually, using a randomly generated key

This key is encrypted using a session key and saved alongside the file
