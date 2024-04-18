import unittest
from flask import Request, Flask
from gitWebhook.webhook import verifyGithubRequest, verifyGitlabRequest, webhookBlueprint
from gitWebhook.functionWebhook import functionWebhookBlueprint
import random
from hmac import new as hmacNew
from hashlib import sha256

VALID_TOKEN = "1234"

class testingRequest(Request):
    def __init__(self, token:str):
        self.data = random.randbytes(50)
        hash_object = hmacNew(token.encode("utf-8"), msg=self.data, digestmod=sha256)
        self.headers = {"X-Hub-Signature-256": f"sha256={hash_object.hexdigest()}", "X-Gitlab-Token":token}
        
    def get_data(self):
        return self.data

class TestVerification(unittest.TestCase):
    def setUp(self) -> None:
        self.validRequest = testingRequest(VALID_TOKEN)
        self.invalidRequest = testingRequest("12345")
        return super().setUp()
    
    def testVerifyGithubRequest(self):
        self.assertTrue(verifyGithubRequest(self.validRequest, VALID_TOKEN))
        self.assertFalse(verifyGithubRequest(self.validRequest, "12345"))
        self.assertFalse(verifyGithubRequest(self.invalidRequest, VALID_TOKEN))
        self.assertFalse(verifyGithubRequest(self.invalidRequest, "12346"))
        
    def testVerifyGitlabRequest(self):
        self.assertTrue(verifyGitlabRequest(self.validRequest, "1234"))
        self.assertFalse(verifyGitlabRequest(self.validRequest, "12345"))
        self.assertFalse(verifyGitlabRequest(self.invalidRequest, "1234"))

# TODO add tests for basic auth

class TestWehbookBlueprint(unittest.TestCase):
    def setUp(self) -> None:
        self.webhook = webhookBlueprint(VALID_TOKEN, name="valid")
        self.app = Flask(__name__)
        self.app.register_blueprint(self.webhook, url_prefix="/valid")
        self.webhookNoToken = webhookBlueprint(None, name="invalid")
        self.app.register_blueprint(self.webhookNoToken, url_prefix="/noToken")
        self.app.config.update({"TESTING": True})
        self.client = self.app.test_client()
        return super().setUp()
    
    def testReceiveWebhookValidGithub(self):
        request = testingRequest(VALID_TOKEN)
        limitedHeaders = {"X-Hub-Signature-256":request.headers["X-Hub-Signature-256"]}
        resp = self.client.post("/valid/", headers=limitedHeaders, data=request.data)
        self.assertEqual(resp.status_code, 415)
        limitedHeaders["Content-Type"] = "application/json"
        resp = self.client.post("/valid/", headers=limitedHeaders, data=request.data)
        self.assertEqual(resp.status_code, 400) #no json
        
    def testReceiveWebhookValidGitlab(self):
        request = testingRequest(VALID_TOKEN)
        limitedHeaders = {"X-Gitlab-Token":request.headers["X-Gitlab-Token"]}
        resp = self.client.post("/valid/", headers=limitedHeaders, data=request.data)
        self.assertEqual(resp.status_code, 415)
        limitedHeaders["Content-Type"] = "application/json"
        resp = self.client.post("/valid/", headers=limitedHeaders, data=request.data)
        self.assertEqual(resp.status_code, 400)
    
    def testReceiveWebhookInvalidNoCheck(self):
        request = testingRequest("123")
        resp = self.client.post("/noToken/", headers=request.headers, data=request.data)
        self.assertEqual(resp.status_code, 415)
        request.headers["Content-Type"] = "application/json"
        resp = self.client.post("/noToken/", headers=request.headers, data=request.data)
        self.assertEqual(resp.status_code, 400)
        
    def testReceiveWebhookInvalidCheckGithub(self):
        request = testingRequest("123")
        limitedHeaders = {"X-Hub-Signature-256":request.headers["X-Hub-Signature-256"]}
        resp = self.client.post("/valid/", headers=limitedHeaders, data=request.data)
        self.assertEqual(resp.status_code, 415)
        limitedHeaders["Content-Type"] = "application/json"
        resp = self.client.post("/valid/", headers=limitedHeaders, data=request.data)
        self.assertEqual(resp.status_code, 401)
    
    def testReceiveWebhookInvalidCheckGitlab(self):
        request = testingRequest("123")
        limitedHeaders = {"X-Gitlab-Token":request.headers["X-Gitlab-Token"]}
        resp = self.client.post("/valid/", headers=limitedHeaders, data=request.data)
        self.assertEqual(resp.status_code, 415)
        limitedHeaders["Content-Type"] = "application/json"
        resp = self.client.post("/valid/", headers=limitedHeaders, data=request.data)
        self.assertEqual(resp.status_code, 401)

    def testOriginBlocking(self):
        request = testingRequest(VALID_TOKEN)
        request.remote_addr = ""
        self.webhook.ipWhitelist = ["192"]
        resp = self.client.post("/valid/", headers=request.headers, data=request.data)
        self.assertEqual(resp.status_code, 403)
        
    def testAppBlocking(self):
        request = testingRequest(VALID_TOKEN)
        limitedHeaders = {"X-Gitlab-Token":request.headers["X-Gitlab-Token"]}
        limitedHeaders["Content-Type"] = "application/json"
        self.webhook.github = False
        resp = self.client.post("/valid/", headers=limitedHeaders, data=request.data)
        self.assertEqual(resp.status_code, 401)
        self.webhook.github = True
        self.webhook.gitlab = False
        resp = self.client.post("/valid/", headers=limitedHeaders, data=request.data)
        self.assertEqual(resp.status_code, 400)
    
    def testProcessWebhook(self):
        self.assertEqual(self.webhook.processWebhook({"test":"test"}), (200, "OK"))
        self.assertEqual(self.webhookNoToken.processWebhook({"test":"test"}), (200, "OK"))

class TestFunctionWebhookBlueprint(unittest.TestCase):
    def setUp(self) -> None:
        func = lambda x: x != x
        self.webhook = functionWebhookBlueprint(VALID_TOKEN, name="valid", functions=[func])
        self.app = Flask(__name__)
        self.app.register_blueprint(self.webhook, url_prefix="/valid")
        self.app.config.update({"TESTING": True})
        self.client = self.app.test_client()
        return super().setUp()
    
    def testReceiveWebhookValid(self):
        request = testingRequest(VALID_TOKEN)
        resp = self.client.post("/valid/", headers=request.headers, data=request.data)
        self.assertEqual(resp.status_code, 415)
        request.headers["Content-Type"] = "application/json"
        resp = self.client.post("/valid/", headers=request.headers, data=request.data)
        self.assertEqual(resp.status_code, 400) #no json
        
    def testReceiveWebhookInvalidCheck(self):
        request = testingRequest("123")
        resp = self.client.post("/valid/", headers=request.headers, data=request.data)
        self.assertEqual(resp.status_code, 415)
        request.headers["Content-Type"] = "application/json"
        resp = self.client.post("/valid/", headers=request.headers, data=request.data)
        self.assertEqual(resp.status_code, 401)
        
    def testProcessWebhook(self):
        self.assertEqual(self.webhook.processWebhook({"test":"test"}), (400, "Function <lambda> returned false"))

if __name__ == "__main__":
    unittest.main()
