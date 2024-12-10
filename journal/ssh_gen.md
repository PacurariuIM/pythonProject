# Generating a SSH key-pair on Win 10/11
- Enter in terminal:
```terminal
ssh-keygen
```
- If using defaults it will save the key in `C:\User[YourUserName].ssh`
- Enter passphrase, write it down or save it somewhere safe
- Keys will be created: public and private
- Enable the option to see hidden files and folders, to see `.ssh`
- The public key, e.g. `"id_rsa.pub."`, is used to authenticate on servers
- To create more keys, just use a different name, e.g. `"id_rsa_github"`
