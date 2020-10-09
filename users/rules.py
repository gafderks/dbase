import rules


@rules.predicate
def is_own_group(user, group):
    """
    Check whether a user belongs to a specified group.
    :param User user:
    :param Group group: use None for all groups
    :return: bool
    """
    if group is None:
        return False
    return user.group == group


@rules.predicate
def view_bookings_from_group(user, group):
    """
    Check whether a user may view a specified game.
    :param User user:
    :param Group group: use None for all groups
    :return: bool
    """
    return user.has_perm("booking.view_other_groups_bookings") | is_own_group(
        user, group
    )
