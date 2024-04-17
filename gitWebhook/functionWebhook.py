from .webhook import webhookBlueprint
from typing import Callable, Any

class functionWebhookBlueprint(webhookBlueprint):
    """A subclass of webhookBlueprint that processes the webhook data using a list of functions. The functions should return True if the webhook data is valid, and False otherwise. If the function returns a string, it will be included in the output."""
    
    def __init__(self, webhookToken: str | None, functions: list[Callable[[dict[str, Any]], bool | str]], *args, **kwargs):
        super().__init__(webhookToken, *args, **kwargs)
        self.functions = functions
        
    def processWebhook(self, data: dict[str, Any]) -> tuple[int, str]:
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
