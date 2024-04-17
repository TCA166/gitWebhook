from abc import ABC, abstractmethod
from flask import Response
from typing import Any

class gitWebhookBlueprintABC(ABC):
    """An abstract class for a webhook blueprint that processes git webhooks."""
    
    @abstractmethod
    def __init__(self, webhookToken:str | None, name:str="webhook", *args, **kwargs):
        ...
    
    @abstractmethod
    def receiveWebhook(self) -> Response:
        ...
    
    @abstractmethod
    def processWebhook(self, data: dict[str, Any]) -> tuple[int, str]:
        ...