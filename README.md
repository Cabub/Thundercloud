# Thundercloud

## Immediate Goals

- Automatic encryption for data-at-rest
- Modular encryption methods so we can easily improve data security going forward
- REST API
- Collect/Store/Transfer as little data as possible

### Initial encryption method: GNUPG

#### Pros

- Well known methodology
- Audited
- FOSS
- Sharing is possible via multiple recipients

#### Cons

- Server side will have access to password and secret key (This means if something gets memory-level access to the box, it could potentially decrypt user's files)
 - Mitigations:
   - Client-side encryption
     - openpgpjs [not great user experience with files]
     - client-side application/browser plugin [larger attack surface, bad trust model]
   - Lock down server
     - This will work for most hosters' threat model, but is not a viable option against determined actors or persistent threats


## Future Goals

- Client-side file encryption
- As close to zero knowledge as possible
 - Use hashes instead of usernames
 - No emails
 - Encrypt everything so that only the user can retrieve it
