from .webhook import webhookBlueprint
from typing import Callable, Any
from logging import Logger

class functionWebhookBlueprint(webhookBlueprint):
    """A subclass of webhookBlueprint that processes the webhook data using a list of functions. The functions should return True if the webhook data is valid, and False otherwise. If the function returns a string, it will be included in the output."""
    
    def __init__(self, webhookToken: str | None, functions: list[Callable[[dict[str, Any]], bool | str]], log:Logger | None = None, name:str="webhook", github:bool=True, gitlab:bool=True, gitea:bool=True, ipWhitelist:list[str] | None = None, *args, **kwargs):
        """Initialize the webhook blueprint with a list of functions to process the webhook data.

        Args:
            webhookToken (str | None): The token used to verify the webhook. If None, no verification is done.
            functions (list[Callable[[dict[str, Any]], bool  |  str]]): List of functions that will process the webhook data.
            log (Logger | None, optional): Optional logger that will be used by this blueprint. Defaults to None.
            name (str, optional): Flask blueprint name. Must be unique. Defaults to "webhook".
            github (bool, optional): Whether the blueprint should process webhook requests from GitHub. Defaults to True.
            gitlab (bool, optional): Whether the blueprint should process webhook requests from GitLab. Defaults to True.
            gitea (bool, optional): Whether the blueprint should process webhook requests from Gitea or other requests using basic auth. Defaults to True.
            ipWhitelist (list[str] | None, optional): Optional whitelist that all incoming requests will be checked against. Defaults to None.
            args: Additional arguments to pass to the Blueprint constructor.
            kwargs: Additional keyword arguments to pass to the Blueprint constructor.
        """
        super().__init__(webhookToken, log, name, github, gitlab, gitea, ipWhitelist, *args, **kwargs)
        self.functions = functions
        
    def processWebhook(self, data: dict[str, Any]) -> tuple[int, str]:
        """Process the webhook data using the list of functions.
        If any function returns False, the process will return a 400 status code.
        If any function returns an invalid type, the process will return a 500 status code.
        Otherwise, the process will return a 200 status code.
        All function outputs are returned to git as a string.

        Args:
            data (dict[str, Any]): The webhook data.

        Returns:
            tuple[int, str]: The status code and message.
        """
        if self.log is not None:
            self.log.debug(f"Processing webhook: {data}")
        output = []
        for function in self.functions:
            res = function(data)
            if isinstance(res, str):
                if self.log is not None:
                    self.log.debug(f"Function {function.__name__} returned a string")
                output.append(res)
            elif isinstance(res, bool):
                if not res:
                    if self.log is not None:
                        self.log.error(f"Function {function.__name__} returned false")
                    return 400, f"Function {function.__name__} returned false"
                else:
                    if self.log is not None:
                        self.log.debug(f"Function {function.__name__} returned true")
                    output.append(str(res))
            else:
                if self.log is not None:
                    self.log.error(f"Function {function.__name__} returned an invalid type")
                return 500, f"Function {function.__name__} returned an invalid type"
        return 200, str(output)
