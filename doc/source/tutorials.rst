Tutorials
==========

Here are some tutorials on how to use gitWebhook.
All tutorials assume you have git installed on your system, and initialized in the directory you are working in.
This repository must be configured to connect via SSH to the remote repository using pre-configured SSH keys so that the webhook can just call::
    
    git pull    

with no issues.

Automatic deployment with GitHub using Webhooks
------------------------------------------------

In this tutorial, we will setup a simple automatic deployment system using GitHub Webhooks.
This will allow you to automatically deploy your code to your server whenever you push to your GitHub repository.

First we are going to set up the backend server that will receive the webhook requests from GitHub.
We need to have gitWebhook installed on the server, so run::

    pip install gitAppWebhook

to make sure you have both Flask and gitWebhook installed.
Then create a new file called `webhook.py` and add the following code::

    from gitWebhook import pullerWebhookBlueprint
    from flask import Flask

    TOKEN = ""

    app = Flask(__name__)
    wb = pullerWebhookBlueprint(token, url_prefix="/")
    app.register_blueprint(wb)

    if __name__ == "__main__":
        app.run()

This code once run will start a Flask server that listens for POST requests on the root URL from either GitHub, GitLab or Gitea using :class:`pullerWebhookBlueprint`.
The `TOKEN` variable is the secret token that you will use to authenticate the requests from GitHub.
You can set this to any string you want, but make sure it is a strong secret.
You can also set the `url_prefix` to any URL you want, but for this tutorial we will use the root URL.

You can now run the server by running the following command::

    python webhook.py

This will start the server on the default Flask url and port.
Naturally if you are running this on a production server, you will want to use a proper WSGI server like Gunicorn or uWSGI.
Flask production deployment is outside the scope of this tutorial, but you can find more information in the `Flask documentation <https://flask.palletsprojects.com/en/1.1.x/deploying/>`_.

After the server is running all that is left is to create a webhook on GitHub.
Go to your repository on GitHub and click on the `Settings` tab.
Then click on the `Webhooks` tab on the left side of the page.
Click on the `Add webhook` button and you will be presented with a form to fill in the details of the webhook.
Don't forget to set the `Content type` to `application/json` and the `Secret` to the same value as the `TOKEN` variable in the `webhook.py` file.

GitHub has a fairly well documented and easy to use webhook interface, so you can find more information on how to set up a webhook on GitHub in the `GitHub documentation <https://developer.github.com/webhooks/creating/>`_.
If you have configured everything correctly you should now be able to push to your repository and see the changes automatically deployed to your server.

How to setup automatic testing with gitWebhook
----------------------------------------------

This example is very similar to the previous one, but alongside deploying the code we will also run tests on the code.
Like previously we will start by setting up the backend server that will receive the webhook requests from GitHub.
We need to have gitWebhook installed on the server, so run::

    pip install gitAppWebhook

and then create a new file called `webhook.py` and add the following code::

    from gitWebhook import pullerWebhookBlueprint
    from flask import Flask
    from tests import yourTestSuite

    TOKEN = ""

    app = Flask(__name__)
    wb = pullerWebhookBlueprint(token, url_prefix="/", tests=yourTestSuite)

    if __name__ == "__main__":
        app.run()

After that you need to create a new file called `tests.py` and add the following code::

    import unittest

    class YourTestSuite(unittest.TestCase):
        def test_something(self):
            self.assertTrue(True)

    yourTestSuite = unittest.TestLoader().loadTestsFromTestCase(YourTestSuite)

This code will start a Flask server that listens for POST requests on the root URL from either GitHub, GitLab or Gitea using :class:`pullerWebhookBlueprint`.
Upon receiving a request, the server will pull the changes from git, run the tests in the `tests.py` file, return the result to GitHub and if the tests failed return the repository to the pre merge state.