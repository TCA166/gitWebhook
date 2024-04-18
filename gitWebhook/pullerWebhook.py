from logging import Logger
from typing import Any
from unittest import TestSuite
from .webhook import webhookBlueprint
from subprocess import run
from unittest import TestSuite, TestResult

class pullerWebhookBlueprint(webhookBlueprint):
    """A subclass of webhookBlueprint that processes the webhook data by pulling from a git repository and running tests."""
    
    def __init__(self, webhookToken: str | None, tests: TestSuite | None = None, log:Logger | None = None, name:str="webhook", github:bool=True, gitlab:bool=True, gitea:bool=True, ipWhitelist:list[str] | None = None, gitCommand: str = "/usr/bin/git", commandEnv: dict[str, str] | None = None, *args, **kwargs):
        """Initialize the webhook blueprint for pulling from a git repository and running tests.

        Args:
            webhookToken (str | None): The token used to verify the webhook. If None, no verification is done.
            tests (TestSuite | None, optional): An optional unittest.TestSuite that will be ran after pulling from git. Defaults to None.
            log (Logger | None, optional): Optional logger that will be used by this blueprint. Defaults to None.
            name (str, optional): Flask blueprint name. Must be unique. Defaults to "webhook".
            github (bool, optional): Whether the blueprint should process webhook requests from GitHub. Defaults to True.
            gitlab (bool, optional): Whether the blueprint should process webhook requests from GitLab. Defaults to True.
            gitea (bool, optional): Whether the blueprint should process webhook requests from Gitea or other requests using basic auth. Defaults to True.
            ipWhitelist (list[str] | None, optional): Optional whitelist that all incoming requests will be checked against. Defaults to None.
            gitCommand (str, optional): Path to the git executable. Defaults to "/usr/bin/git".
            commandEnv (dict[str, str] | None, optional): Optional environment that will be used by git during pulling. Defaults to None.
        """
        super().__init__(webhookToken, log, name, github, gitlab, gitea, ipWhitelist, *args, **kwargs)
        self.tests = tests
        self.gitCommand = gitCommand
        if commandEnv is None:
            commandEnv = dict(GIT_SSH_COMMAND="/usr/bin/ssh")
        self.commandEnv = commandEnv
    
    def processWebhook(self, data: dict[str, Any]) -> tuple[int, str]:
        """Process the webhook data by pulling from a git repository and running tests.
        If the tests are not provided, only the pull will be done.
        Otherwise the tests will be ran and if they fail the merge will be aborted.

        Args: 
            data (dict[str, Any]): The webhook data.

        Returns:
            tuple[int, str]: The status code and message.
        """
        if self.log is not None:
            self.log.debug(f"Processing webhook: {data}")
        process = run([self.gitCommand, "pull"], env=self.commandEnv)
        if process.returncode != 0:
            if self.log is not None:
                self.log.error(f"Error while pulling: {process.stderr.decode('utf-8')}")
            return 500, process.stderr.decode("utf-8")
        if self.tests is not None:
            if self.log is not None:
                self.log.debug("Running tests")
            result = TestResult()
            self.tests.run(result) # Why does this method want a TestResult object? Why can't it just return the result?
            if result.wasSuccessful():
                if self.log is not None:
                    self.log.info(f"{result.testsRun} tests passed ")
                return 200, "Tests passed"
            else:
                abortProcess = run([self.gitCommand, "merge", "--abort"], env=self.commandEnv)
                if self.log is not None:
                    self.log.error(f"Tests did not pass, Errors: {result.errors}, Failures: {result.failures}. Merge abort status: {abortProcess.returncode}")
                return 428, f"Tests did not pass, Errors: {result.errors}, Failures: {result.failures}. Merge abort status: {abortProcess.returncode}"
        else:
            return 200, "Webhook received successfully"
    