# githubWebhook

A Flask blueprint for receiving GitHub or GitLab webhooks.

## Setup

1. Clone this repo
2. Install packages from requirements.txt
3. Register the webhookBlueprint within a Flask app of your choice
4. Now you just need to setup the webhook on the git side, and you are done

## Default behavior

The default webhookBlueprint requires a git token to be provided for verification.
For GitHub that would be the secret string that you provide [during creation](https://docs.github.com/en/webhooks/using-webhooks/creating-webhooks#creating-a-repository-webhook) and for GitLab that would be the [secret token](https://docs.gitlab.com/ee/user/project/integrations/webhooks.html#validate-payloads-by-using-a-secret-token).
webhookBlueprint creates a POST endpoint / which receives webhook requests, verifies them and passes their JSON content to webhookBlueprint.processWebhook().
webhookBlueprint.processWebhook() by default creates a new git subprocess that performs a git pull.
After the git pull the default method attempts to run an optionally provided unittest.TestSuite.
If these tests fail the method attempts to abort the last merge.
The results of the tests and the abort merge is returned to git.
For security reasons only webhooks with means of verification will be accepted.

## Customization

The class was built with customization in mind.
If you need the processing method to do something else I suggest you simply override the processWebhook method with your own method in the singleton blueprint instance.
Alternatively if you really need to build upon the blueprint, or want a different interface you can always just create a subclass.
