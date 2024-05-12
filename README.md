# gitWebhook

[![PyPI - Downloads](https://img.shields.io/pypi/dm/gitAppWebhook)](https://pypi.org/project/gitAppWebhook/)
[![GitHub Pages Documentation](https://img.shields.io/badge/GitHub_Pages-Documentation-blue)](https://tca166.github.io/gitWebhook/)

A Python library providing [Flask blueprints](https://flask.palletsprojects.com/en/3.0.x/blueprints/) for receiving GitHub, GitLab or Gitea webhooks and acting upon them.
The library provides webhooks allowing for automatic deployment, testing and integrations.
However due to the open ended nature of the blueprint this behavior can be easily customized thanks to the very open ended class dependency tree.

## Setup

1. Setup the webhook on the git side
   During the setup be sure to pay close attention to any opportunities to input any sort of secret key.
   You will need that key later if you want to enable webhook verification **THIS IS SOMETHING THAT I GREATLY ADVISE YOU DO**.
   For GitHub that would be the secret string that you provide [during creation](https://docs.github.com/en/webhooks/using-webhooks/creating-webhooks#creating-a-repository-webhook), for GitLab that would be the [secret token](https://docs.gitlab.com/ee/user/project/integrations/webhooks.html#validate-payloads-by-using-a-secret-token) and for Gitea that would be the [authorization token](https://docs.gitea.com/usage/webhooks#authorization-header).
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

    While installing the pip package functions as any other package the thing with this repo folder is that it functions like a local package.
    That means that cloning this repo into your project folder will allow you to import ```gitWebhook``` as if it was installed via pip.
    Same applies with adding as submodule with the added benefit of git understanding what is going on better,

3. Create an instance of ```webhookBlueprint``` (or either of it's subclasses) with your settings

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

## Blueprint classes

This library provides a basic blueprint derived class for only receiving webhooks and a few derived classes with different webhook processing capabilities.

### webhookBlueprint

This very basic class itself has no webhook processing capabilities, but functions as a base from which webhook receiving blueprints may be derived from.
It fully implements all the verification required for GitHub and GitLab blueprints and as such should be the class you should derive from.

#### webhookBlueprint behavior

1. Verifies the request's validity (Optional but very recommended)
2. Returns 200

### pullerWebhookBlueprint

This class derived from ```webhookBlueprint``` is aimed to be used as a means of automating deployment and testing on servers.
If you don't want to use GitHub actions, you can always use a Flask app with this blueprint registered.

#### pullerWebhookBlueprint behavior

Upon receiving a ```POST``` request to the / endpoint the blueprint:

1. Verifies the request's validity (Optional but very recommended)
2. Performs a ```git pull```
3. Runs a test suite (Optional)
    1. If the tests failed it tries to revert the pull
4. Returns to GitHub or GitLab the results of the pull and tests if they have been performed

### functionWebhookBlueprint

This class derived from ```webhookBlueprint``` is aimed to be used as a means of integrating different services.
You provide it on initialization with a list of ```Callable``` taking in webhook payloads as a single argument, and these functions will be called upon receiving a webhook.
Thus you can easily integrate services with this class by simply having integration happen in such a ```Callable```.

#### functionWebhookBlueprint behavior

Upon receiving a ```POST``` request to the / endpoint the blueprint:

1. Verifies the request's validity (Optional but very recommended)
2. Calls all functions contained within it's ```functions``` list
3. If any returned False it returns a failure to origin.

### Customization

You can easily tweak any of the classes to your liking in two ways.

1. Some settings can be tweaked during blueprint instance creation.
    You can:
    - enable or disable webhook verification by providing (or not providing) a ```webhookToken```
    - enable unit test running by providing a ```unittest.testSuite``` instance (pullerWebhookBlueprint)
    - enable logging by providing a ```logging.Logger``` instance
    - change blueprint name to avoid conflicts during blueprint registration
    - limit the blueprints to accept webhooks only from one git app or multiple
    - limit the blueprints to accept incoming webhooks only from whitelisted IPs
    - change the command used to invoke git (pullerWebhookBlueprint)
    - change the OS environment used by child git processes (pullerWebhookBlueprint)
2. More advanced changes require creating a subclass from webhookBlueprint
    This isn't that daunting.
    There are two methods in the class: ```receiveWebhook``` and ```processWebhook```.
    Override the former to change how the raw request is handled and verified.
    Override the latter to change what is done once the webhook is verified.

## License

This work is licensed under the MIT license.
