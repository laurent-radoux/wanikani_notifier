Usage
-----

To use WaniKani Notifier in a project::

    from wanikani_api.client import Client as WaniKaniClient

    from wanikani_notifier import wanikani
    from wanikani_notifier.notifiers.pushover import PushoverNotifier

    notifiers = []
    notifiers.append(notifier.factory.create(PushoverNotifier.key(), app_token="__APP_TOKEN__", user_token="__USER_TOKEN__"))
    # ...can add more notifiers if need be...

    wanikani.notify_available_assignments(WaniKaniClient("__WANIKANI_API_TOKEN__"), since, notifiers)

To use WaniKani Notifier command line interface::

    wanikani_notifier --wanikani=__TOKEN__ --stop-if-empty available_assignments_now --since=1 all_available_assignments notify --console [--pushover=__APP_TOKEN__ __USER_TOKEN__]
