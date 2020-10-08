class UserAlertException(Exception):
    """
    Used for exceptions that are appropriate to propagate to the user.
    """

    # TODO allow passing a status code e.g. forbidden or not found
    # TODO allow passing a color for the alert (default warning/danger)
    pass
