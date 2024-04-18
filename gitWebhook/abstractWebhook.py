from abc import ABC, abstractmethod
from flask import Response
from typing import Any

class gitWebhookBlueprintABC(ABC):
    """An abstract class for a webhook blueprint that processes git webhooks."""
    
    @abstractmethod
    def __init__(self, webhookToken:str | None, name:str="webhook", *args, **kwargs):
        """Initialize the webhook blueprint, register the recieveWebhook method as a POST endpoint.

        Args:
            webhookToken (str | None): The token used to verify the webhook. If None, no verification is done.
            name (str, optional): Unique blueprint name. Defaults to "webhook".
            args: Additional arguments to pass to the Blueprint constructor.
            kwargs: Additional keyword arguments to pass to the Blueprint constructor.
        """
        ...
    
    @abstractmethod
    def receiveWebhook(self) -> Response:
        """Method that acts as a POST endpoint for the webhook blueprint.

        Returns:
            Response: The response to the webhook request.
        """
        ...
    
    @abstractmethod
    def processWebhook(self, data: dict[str, Any]) -> tuple[int, str]:
        """Process the webhook data and return a status code and message.

        Args:
            data (dict[str, Any]): The webhook data.

        Returns:
            tuple[int, str]: The status code and message.
        """
        ...