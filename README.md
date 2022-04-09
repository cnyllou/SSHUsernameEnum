# SSHUsernameEnum
SSH Username enumeration when the only available credential is the SSH private key

Lost & Found key owner SSH brute-force

Brute-force a username for a found SSH private key.

## PREREQUISITES

- For development I use 3.10.2 (Use this if your version is not working)
- Minimal version should be 3.7, because of typing 

Commands to run

```bash
python -m venv venv
. venv/bin/activate
python -m pip install -r requirements.txt
```

## USAGE

```bash
$ python ssh-key-user-enum.py username.wordlist.txt
```

## NOTE

Edit hostname and key_filename!
