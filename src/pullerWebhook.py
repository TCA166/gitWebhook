from logging import Logger
from typing import Any
from unittest import TestSuite
from src.webhook import webhookBlueprint
from subprocess import run
from unittest import TestSuite, TestResult

class pullerWebhookBlueprint(webhookBlueprint):
    """A subclass of webhookBlueprint that processes the webhook data by pulling from a git repository and running tests."""
    def __init__(self, webhookToken: str | None, tests: TestSuite | None = None, log: Logger | None = None, name: str = "webhook", gitCommand: str = "/usr/bin/git", commandEnv: dict[str, str] | None = None, *args, **kwargs):
        super().__init__(webhookToken, log, name, *args, **kwargs)
        self.tests = tests
        self.gitCommand = gitCommand
        if commandEnv is None:
            commandEnv = dict(GIT_SSH_COMMAND="/usr/bin/ssh")
        self.commandEnv = commandEnv
    def processWebhook(self, data: dict[str, Any]) -> tuple[int, str]:
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
    