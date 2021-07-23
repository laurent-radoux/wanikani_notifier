=====
Usage
=====

To use WaniKani Notifier in a project::

    from wanikani_api.client import Client as WaniKaniClient

    from wanikani_notifier import wanikani_notifier
    from wanikani_notifier.notifiers.pushsafer import PushSaferNotifier

    notifiers = []
    notifiers.append(PushSaferNotifier("__PUSHSAFER_KEY__"))
    # ...can add more notifiers if need be...

    wanikani_notifier.notify_available_assignments(WaniKaniClient("__WANIKANI_API_TOKEN__"), since, notifiers)

To use WaniKani Notifier command line interface::

    wanikani_notifier --wanikani=__TOKEN__ --since=1 [--pushsafer=__TOKEN__]
