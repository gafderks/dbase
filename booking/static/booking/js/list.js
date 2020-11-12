import BookingContainer from './booking-container.js';

/* global gettext, ngettext */

export default class List extends BookingContainer {

  constructor($elem, partOfDay) {
    super($elem, partOfDay);
    this._groupOverlappingBookings();
    this._attachEvents();
  }

  // eslint-disable-next-line no-unused-vars
  onBookingChanged(booking) {
    this._regroupBookings();
  }

  addBooking(booking) {
    super.addBooking(booking);
    this._regroupBookings();
  }

  removeBooking(booking) {
    super.removeBooking(booking);
    this._regroupBookings();
  }

  _findOverlappingBookings() {
    const result = [];
    let prev = null;
    let duplicates = [];

    for (let booking of this._bookings) {
      // Skip bookings of custom materials
      if (booking.material_id === '') {
        continue;
      }
      // If the previous is null (holds for first booking): add to duplicates and continue
      if (prev === null) {
        duplicates.push(booking);
        prev = booking;
        continue;
      }
      // If the booking is different from the previous booking: no more duplicates
      if (booking.material_id !== prev.material_id) {
        // If the duplicates are more than one, add to the result
        if (duplicates.length > 1) {
          result.push(duplicates);
        }
        // Add this booking to the duplicates.
        duplicates = [booking];
      } else {
        // If the booking is the same as the previous: add duplicate
        duplicates.push(booking);
      }
      prev = booking;
    }

    // For last booking check if duplicates are more than one, add to the result
    if (duplicates.length > 1) {
      result.push(duplicates);
    }

    return result;
  }

  _regroupBookings() {
    this._ungroupBookings();
    this._groupOverlappingBookings();
  }

  _ungroupBookings() {
    // Show booking duplicates again
    this._$elem.find('.booking-duplicate').removeClass('booking-duplicate d-none').addClass('d-flex');
    // Remove handlers
    this._$elem.find('.booking-duplicate-handler').remove();
  }

  _groupOverlappingBookings() {
    const duplicates_sets = this._findOverlappingBookings();
    for (let duplicates_set of duplicates_sets) {
      // Prepare the texts that should go on the handler
      // Total number of materials
      const amounts = duplicates_set.map(booking => booking.amount);
      let total_amounts;
      if (amounts.some(isNaN)) {
        // Show dots if some of the amounts is not numerical
        total_amounts = '...';
      } else {
        // Sum the amounts
        total_amounts = amounts.reduce((a, b) => a + b, 0);
      }
      // Number of games
      const num_games = new Set(duplicates_set.map(booking => booking.game_id)).size;
      // Number of groups
      const groups = new Set(duplicates_set.map(booking => booking.group_id));
      // Text for number of groups
      let groups_text = '';
      if (groups.size > 0 && !groups.has(undefined)) {
        groups_text = `${groups.size} ${ngettext('group', 'groups', groups.size)}, `;
      }
      // Text for total number of materials
      const bookings_text = `${duplicates_set.length} ${gettext('bookings')}`;
      // Text for number of groups plus number of games
      const games_text = `${groups_text}${num_games} ${ngettext('game', 'games', num_games)}`;
      // Text for stock
      const stock = duplicates_set[0].stock;
      const stock_placeholder = stock ? `${gettext('Stock')}: ${stock}` : '';
      const stock_text = stock ? `<i class="fas fa-store-alt"></i> ${stock}` : '';
      const duplicate_bar = $('<tr>').addClass('booking booking-duplicate-handler d-flex flex-wrap fix-anchor')
        .append(
          $('<td>').addClass('booking-duplicate-dir col-auto pl-md-3 pl-sm-2 d-flex align-items-center')
            .html('<i class="far fa-folder fa-fw"></i><i class="far fa-folder-open fa-fw"></i>'),
          duplicates_set[0].elem.find('.booking-material').clone(),
          stock ?
            $('<td>').addClass('col-2')
              .append(
                $('<div>').addClass('text-truncate').attr({
                  'title': total_amounts, 'data-toggle': 'tooltip', 'data-placement': 'left'
                }).text(total_amounts),
                $('<div>').addClass('small text-muted text-truncate').attr({
                  'title': stock_placeholder, 'data-toggle': 'tooltip', 'data-placement': 'left'
                }).html(stock_text),
              ) :
            $('<td>').addClass('d-flex align-items-center col-2').text(total_amounts),
          $('<td>').addClass('col-4 col-md')
            .append(
              $('<div>').addClass('text-truncate').attr({
                'title': bookings_text, 'data-toggle': 'tooltip', 'data-placement': 'left'
              }).text(bookings_text),
              $('<div>').addClass('small text-muted text-truncate').attr({
                'title': games_text, 'data-toggle': 'tooltip', 'data-placement': 'left'
              }).text(games_text),
            )
        ).click(
          ev => {
            $(ev.currentTarget).toggleClass('open');
            for (let duplicate of duplicates_set) {
              duplicate.elem.toggleClass('d-flex d-none');
            }
          }
        );
      // remove label relationship
      duplicate_bar.find('label').attr('for', '');
      // remove material modal
      duplicate_bar.find('[data-target="#catalogModal"]').removeAttr('data-target data-toggle data-catalog-item role');
      duplicates_set[0].elem.before(duplicate_bar);
      for (let duplicate of duplicates_set) {
        duplicate.elem.addClass('booking-duplicate d-none').removeClass('d-flex');
      }
    }
  }
}
