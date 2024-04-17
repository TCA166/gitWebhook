# githubWebhook

A Flask blueprint for receiving GitHub or GitLab webhooks and acting upon them.
By default the blueprint performs a git pull and optionally ```unittest.testSuite``` tests upon receiving a valid webhook request.
The idea behind this is to allow for automatic testing or deployment without using GitHub Actions.
However due to the open ended nature of the blueprint this behavior can be easily customized.

## Setup

1. Setup the webhook on the git side
   During the setup be sure to pay close attention to any opportunities to input any sort of secret key.
   You will need that key later if you want to enable webhook verification **THIS IS SOMETHING THAT I GREATLY ADVISE YOU DO**.
   For GitHub that would be the secret string that you provide [during creation](https://docs.github.com/en/webhooks/using-webhooks/creating-webhooks#creating-a-repository-webhook) and for GitLab that would be the [secret token](https://docs.gitlab.com/ee/user/project/integrations/webhooks.html#validate-payloads-by-using-a-secret-token).
2. Install this package
    - Using pip

        ```sh
        pip install gitAppWebhook
        ```

    - By cloning the repository

        ```sh
        git clone https://github.com/TCA166/gitWebhook.git
        pip install -r gitWebhook/requirements.txt
        ```

    - By including this repo as a submodule

        ```sh
        git submodule add https://github.com/example/repo.git gitWebhook
        pip install -r gitWebhook/requirements.txt
        ```

3. Create an instance of ```webhookBlueprint``` with your settings

    ```python3
    import gitWebhook

    wb = gitWebhook.webhookBlueprint(token, url_prefix="/")
    ```

4. Register the instance within a Flask app of your choice

    ```python3
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(wb)
    ```

If you are lost you can always look at official GitHub resources, or look at [wsgi.py](./wsgi.py) where an example configured Flask webapp is located.

## webhookBlueprint class

The webhook receiving behavior was packaged together as a single class derived from the Flask blueprint class.

### Default behavior

Upon receiving a ```POST``` request to the / endpoint the blueprint:

1. Verifies the request's validity (Optional but very recommended)
2. Performs a ```git pull```
3. Runs a test suite (Optional)
    1. If the tests failed it tries to revert the pull
4. Returns to GitHub or GitLab the results of the pull and tests if they have been performed

### Customization

You can easily tweak the class to your liking in two ways.

1. Some settings can be tweaked during blueprint instance creation.
    You can:
    - enable or disable webhook verification by providing (or not providing) a ```webhookToken```
    - enable unit test running by providing a ```unittest.testSuite``` instance
    - enable logging by providing a ```logging.Logger``` instance
    - change blueprint name to avoid conflicts during blueprint registration
    - change the command used to invoke git
    - change the OS environment used by child git processes
2. More advanced changes require creating a subclass from webhookBlueprint
    This isn't that daunting.
    There are two methods in the class: ```receiveWebhook``` and ```processWebhook```.
    Override the former to change how the raw request is handled and verified.
    Override the latter to change what is done once the webhook is verified.

## License

[![CCimg](https://i.creativecommons.org/l/by/4.0/88x31.png)](http://creativecommons.org/licenses/by/4.0/)  
This work is licensed under a [Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/).  
