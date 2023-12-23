from flask import Blueprint, request, Response, abort, Request
from hashlib import sha256
from hmac import new as hmacNew
from subprocess import run
from unittest import TestSuite, TestResult

def verifyGithubSignature(request: Request, token:str) -> bool:
    """Verify the GitHub signature of a webhook request"""
    signature = request.headers.get("X-Hub-Signature-256")
    if signature is None:
        return False
    hash_object = hmacNew(token.encode("utf-8"), msg=request.get_data(), digestmod=sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    return signature == expected_signature

class webhookBlueprint(Blueprint):
    """Wrapper over the flask blueprint that creates an endpoint for receiving and processing git webhooks. Overwrite the processWebhook method to process the webhook data."""
    def __init__(self, webhookToken:str, tests:TestSuite=None, name:str="webhook", import_name:str=__name__, *args, **kwargs):
        super().__init__(name, import_name, *args, **kwargs)
        self.webhookToken = webhookToken
        self.tests = tests
        self.route("/", methods=["POST"])(self.receiveWebhook)
    def receiveWebhook(self) -> Response:
        """Receive webhook from GitHub and process it using the processWebhook method."""
        if "X-Hub-Signature-256" in request.headers:
            if not verifyGithubSignature(request, self.webhookToken):
                abort(401)
        elif "X-Gitlab-Token":
            if request.headers.get("X-Gitlab-Token") != self.token:
                abort(401)
        else:
            abort(400, "Unsupported webhook source")
        #at this point the webhook is verified
        return self.processWebhook(request.json)
    def processWebhook(self, data:dict) -> tuple[int, str]:
        """Process the webhook. Return a tuple of (status code, message)"""
        process = run(["/usr/bin/git", "pull"], env=dict(GIT_SSH_COMMAND="/usr/bin/ssh"))
        if process.returncode != 0:
            return 500, process.stderr.decode("utf-8")
        if self.tests is not None:
            result:TestResult = self.tests.run()
            if result.wasSuccessful():
                return 200, "Tests passed"
            else:
                abortProcess = run(["/usr/bin/git", "merge", "--abort"], env=dict(GIT_SSH_COMMAND="/usr/bin/ssh"))
                return 428, f"Tests did not pass, Errors: {result.errors}, Failures: {result.failures}. Merge abort status: {abortProcess.returncode}"
        else:
            return 200, "Webhook received successfully"
        
if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(webhookBlueprint("token"))
    app.run()
