gitWebhook
==========

.. toctree::
   :maxdepth: 4

   gitWebhook

Webhook Configuration Options
-----------------------------

The classes contained in this module share some common configuration options that allow you to customize the behavior of the webhook.
This occurs via arguments passed to the classes during instantiation.
Since all webhook blueprint classes inherit from :class:`webhookBlueprint`, the configuration options are shared among all classes.

The following configuration options are available:

- **webhookToken** (*str*) - The secret key that the webhook will use to verify the authenticity of incoming requests.
- **log** (*logging.Logger*) - The logger that the webhook will use to log messages.
- **name** (*str*) - The name of the webhook blueprint.
- **github** (*bool*) - Whether the webhook should support GitHub webhooks.
- **gitlab** (*bool*) - Whether the webhook should support GitLab webhooks.
- **gitea** (*bool*) - Whether the webhook should support Gitea webhooks.
- **ipWhitelist** (*List[str]*) - A list of IP addresses that are allowed to send requests to the webhook.

None of these options are mandatory, but you should at least provide a `webhookToken` to ensure that the webhook is secure.

Logging
-------

All of the blueprints in this module will log events to the provided logger if one is provided.
All internal errors are logged at the `ERROR` level.
Arrival of a request is logged at the `INFO` level.
While all failed requests are logged at the `WARNING` level.
Use this information to filter what sort of events you want to receive.

