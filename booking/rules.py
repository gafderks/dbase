import rules

from users.rules import is_own_group


# Event rules


@rules.predicate
def view_event(user, event):
    """
    Check whether a user may view a specified event.
    :param User user:
    :param Event event:
    :return: bool
    """
    if event is None:
        return None
    return user.has_perm("booking.view_hidden_events") or event.visible is True


@rules.predicate
def book_on_event(user, event):
    """
    Check whether a user may book on a specified event.
    :param User user:
    :param Event event:
    :return: bool
    """
    if event is None:
        return user.has_perm("booking.book_on_event")
    if event.is_locked and not user.has_perm("booking.book_on_locked_events"):
        return False
    if event.is_privileged and not user.has_perm("booking.book_on_privileged_events"):
        return False
    return True


# Game rules
@rules.predicate
def is_game_from_own_group(user, game):
    """
    Check whether a game is from the group that the user is part of.
    :param User user:
    :param Game game:
    :return: bool
    """
    return is_own_group(user, game.group)


@rules.predicate
def book_on_game(user, game):
    """
    Check whether a user may change a game.
    A user may only change a game if it may change the event that it is attached to and
    either the game is from the users own group or the user has permission to change
    bookings from other groups.
    :param User user:
    :param Game game:
    :return: bool
    """
    return (
        book_on_event(user, game.event)
        & view_game(user, game)
        & (
            is_game_from_own_group(user, game)
            | user.has_perm("booking.change_other_groups_bookings")
        )
    )


@rules.predicate
def change_game(user, game):
    """
    Check whether a user may change a specified game.
    Note: This is an alias to book_on_game at the moment.
    :param User user:
    :param Game game:
    :return: bool
    """
    return book_on_game(user, game)


@rules.predicate
def add_game_to_group(user, group):
    """
    Check whether a user is allowed to add a game to the specified group.
    Note: Does not check for if event is editable. But later change_game does check
    this.
    :param User user:
    :param Group group:
    :return: bool
    """
    return is_own_group(user, group) | user.has_perm(
        "booking.change_other_groups_bookings"
    )


@rules.predicate
def view_game(user, game):
    """
    Check whether a user may view a specified game.
    :param User user:
    :param Game game:
    :return: bool
    """
    return view_event(user, game.event) & (
        is_game_from_own_group(user, game)
        | user.has_perm("booking.view_others_groups_bookings")
    )


# Booking rules
@rules.predicate
def is_booking_from_own_group(user, booking):
    """
    Check whether a the game of a booking is from the group that the user is part of.
    :param User user:
    :param Booking booking:
    :return: bool
    """
    return is_own_group(user, booking.game.group)


@rules.predicate
def change_booking(user, booking):
    """
    Check whether a user may edit a specific booking.
    :param User user:
    :param Booking booking:
    :return: bool
    """
    return book_on_game(user, booking.game)


@rules.predicate
def view_booking(user, booking):
    """
    Check whether a user may view a specified booking.
    :param User user:
    :param Booking booking:
    :return: bool
    """
    return view_game(user, booking.game)
