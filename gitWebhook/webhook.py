from flask import Blueprint, request, Response, abort, Request
from hashlib import sha256
from hmac import new as hmacNew
from typing import Any, Callable
from logging import Logger
from .abstractWebhook import gitWebhookBlueprintABC

GITHUB_HEADER = "X-Hub-Signature-256"

GITLAB_HEADER = "X-Gitlab-Token"

def verifyGithubRequest(request: Request, token:str) -> bool:
    """Verify the GitHub signature of a webhook request"""
    signature = request.headers.get(GITHUB_HEADER)
    if signature is None:
        return False
    hash_object = hmacNew(token.encode("utf-8"), msg=request.get_data(), digestmod=sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    return signature == expected_signature

def verifyGitlabRequest(request: Request, token:str) -> bool:
    """Verify the GitLab token of a webhook request"""
    return request.headers.get(GITLAB_HEADER) == token

def verifyBasicAuth(request: Request, token:str) -> bool:
    """Verify the basic authorization of a webhook request"""
    return str(request.authorization) == token

# TODO add automatic github IP whitelisting

class webhookBlueprint(Blueprint, gitWebhookBlueprintABC):
    """Wrapper over the flask blueprint that creates an endpoint for receiving and processing git webhooks. Overwrite the processWebhook method to process the webhook data."""
    
    def __init__(self, webhookToken:str | None, log:Logger | None = None, name:str="webhook", github:bool=True, gitlab:bool=True, gitea:bool=True, ipWhitelist:list[str] | None = None, *args, **kwargs):
        """Initailize the webhook blueprint, register the recieveWebhook method as a POST endpoint.

        Args:
            webhookToken (str | None): The token used to verify the webhook. If None, no verification is done.
            log (Logger | None, optional): Optional logger that will be used by this blueprint. Defaults to None.
            name (str, optional): Flask blueprint name. Must be unique. Defaults to "webhook".
            github (bool, optional): Whether the blueprint should process webhook requests from GitHub. Defaults to True.
            gitlab (bool, optional): Whether the blueprint should process webhook requests from GitLab. Defaults to True.
            gitea (bool, optional): Whether the blueprint should process webhook requests from Gitea or other requests using basic auth. Defaults to True.
            ipWhitelist (list[str] | None, optional): Optional whitelist that all incoming requests will be checked against. Defaults to None.
            args: Additional arguments to pass to the Blueprint constructor.
            kwargs: Additional keyword arguments to pass to the Blueprint constructor.
        """
        
        super().__init__(name, self.__class__.__name__, *args, **kwargs)
        self.log = log
        if webhookToken is None:
            if self.log is not None:
                self.log.warning("No webhook token provided. THIS IS VERY UNSAFE")
        self.webhookToken = webhookToken
        self.github = github
        self.gitlab = gitlab
        self.gitea = gitea
        self.ipWhitelist = ipWhitelist
        self.hooks = []
        self.route("/", methods=["POST"])(self.receiveWebhook)
    
    def receiveWebhook(self) -> Response:
        if self.ipWhitelist is not None:
            if request.remote_addr is None:
                if self.log is not None:
                    self.log.warning("Received a request with no IP address")
                abort(403)
            if request.remote_addr not in self.ipWhitelist:
                if self.log is not None:
                    self.log.warning(f"Received a request from an unauthorized IP address: {request.remote_addr}")
                abort(403)
        if self.log is not None:
            self.log.debug("Received a POST request to the webhook endpoint")
        #check if the content type is json
        if request.content_type != "application/json":
            if self.log is not None:
                self.log.warning(f"A request with an invalid content type: {request.content_type}")
            abort(415)
        if self.webhookToken is not None: #verification
            if GITHUB_HEADER in request.headers and self.github:
                if not verifyGithubRequest(request, self.webhookToken):
                    if self.log is not None:
                        self.log.warning("A request with an invalid GitHub signaturez")
                    abort(401)
            elif GITLAB_HEADER in request.headers and self.github:
                if not verifyGitlabRequest(request, self.webhookToken):
                    if self.log is not None:
                        self.log.warning("A request with an invalid GitLab token")
                    abort(401)
            elif request.authorization is not None and self.gitea: # basic authorization which is what Gitea uses
                if not verifyBasicAuth(request, self.webhookToken):
                    if self.log is not None:
                        self.log.warning("A request with an invalid basic authorization")
                    abort(401)
            else:
                if self.log is not None:
                    self.log.warning("A request with no signature found")
                abort(401) #no feedback, in case somebody is trying to guess the token
        #logs beforehand were warnings, so that messages regarding unauthorized requests can be filtered
        for hook in self.hooks:
            hook()
        data = request.json
        if data is None or not isinstance(data, dict):
            if self.log is not None:
                self.log.error("A request with invalid JSON")
            abort(400, "Invalid JSON")
        #at this point the webhook is verified
        ret = self.processWebhook(data)
        if self.log is not None:
            self.log.info(f"Webhook processed with status code {ret[0]} and message: {ret[1]}")
        return Response(ret[1], status=ret[0])
    
    def processWebhook(self, data:dict[str, Any]) -> tuple[int, str]:
        """Process the webhook. Return a tuple of (status code, message)

        Args:
            data (dict[str, Any]): The webhook data
        
        Returns:
            tuple[int, str]: HTTP return code with a message
        """
        return (200, "OK")
    
    def hook(self, func:Callable[..., Any]) -> Callable[..., Any]:
        """Adds a function to the list of functions that will be called when a webhook is received.
        This is different from what functionWebhook functions do as this function is called before the processWebhook method and the return value is not checked.
        
        Args:
            func (Callable): The function to add to the list of functions that will be called when a webhook is received.
        """
        self.hooks.append(func)
        def inner(*args, **kwargs):
            print("test")
            if self.log is not None:
                self.log.debug("Received a POST request to a hooked function")
            return func(*args, **kwargs)
        return inner
