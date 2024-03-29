# VorishkaBot2.0

> 🦺 This project is currently under construction. The stable version is available [here](https://github.com/MrGauz/VorishkaBot/tree/1.0).

## Running the bot locally

1. Install the dependencies with ``pip install -r requirements.txt``
2. Create a ``.env`` file (see [``.env.example``](./.env.example)) and fill in the values
3. Run the bot with ``python3 main.py``

## Setting up CI/CD pipeline

1. Create a new SSH key pair with ``ssh-keygen -t ed25519``
2. Add the public key to ``~/.ssh/authorized_keys`` on the target server
3. Create Repository secrets for deployment in the repository:
   - ``REMOTE_SERVER`` 
   - ``REMOTE_USER``
   - ``REMOTE_PATH``
   - ``SSH_PRIVATE_KEY``
   - ``TOKEN``
4. Create a deployment repository on the target server
   - ``mkdir -p /bots/VorishkaBot2.0``
   - ``touch /bots/VorishkaBot2.0/context_data``
5. Create an ``.env`` file in ``/bots/VorishkaBot2.0/`` (see [``.env.example``](./.env.example)) and fill in the values

## License

This work is licensed under [CC BY-NC 4.0](LICENSE.md). 
