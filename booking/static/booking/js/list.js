import Booking from './booking.js';

export default class List {

  constructor($elem, partOfDay) {
    this._$elem = $elem;
    this._partOfDay = partOfDay;
    this._partOfDayCode = $elem.data('part-of-day-code');

    this._bookings = this._constructBookings();
    this._attachEvents();
    this._groupOverlappingBookings();
  }

  collapse() {
    this._$elem.find('.card-body').collapse('hide');
  }

  show() {
    this._$elem.find('.card-body').collapse('show');
  }

  toggleCollapse() {
    this._$elem.find('.card-body').collapse('toggle');
  }

  _constructBookings() {
    let bookings = [];
    this._$elem.find('.booking').each((i, elem) => {
      const booking = new Booking($(elem), this);
      $(elem).data('booking', booking);
      bookings.push(booking);
    });
    if (bookings.length === 0) {
      this._$elem.find('.bookings-table thead').addClass('d-none');
    }
    return bookings;
  }

  _populateFromDOM() {
    this.partOfDayCode = this._$elem.data('part-of-day-code') || this._partOfDayCode;
  }

  get elem() {
    return this._$elem;
  }

  _attachEvents() {
    // Tooltip
    this._$elem.find('[data-toggle="tooltip"]').tooltip();
    // Toggle collapse
    this._$elem.find('.list-name').click(_ => this.toggleCollapse());
  }

  // eslint-disable-next-line no-unused-vars
  onBookingChanged(booking) {
    this._regroupBookings();
  }

  addBooking(booking) {
    this._bookings.push(booking);
    booking.elem.appendTo(this._$elem.find('.bookings-table').find('tbody'));
    this._$elem.find('.bookings-table thead').removeClass('d-none');
    this._regroupBookings();
  }

  removeBooking(booking) {
    booking.elem.detach();
    this._bookings = this._bookings.filter(bk => bk.id !== booking.id);
    if (this._bookings.length === 0) {
      this._$elem.find('.bookings-table thead').addClass('d-none');
    }
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
      const amounts = duplicates_set.map(booking => booking.amount);
      let total_amounts;
      if (amounts.some(isNaN)) {
        // Show dots if some of the amounts is not numerical
        total_amounts = '...';
      } else {
        // Sum the amounts
        total_amounts = amounts.reduce((a, b) => a + b, 0);
      }
      const duplicate_bar = $('<tr>').addClass('booking booking-duplicate-handler d-flex flex-wrap')
        .append(
          $('<td>').addClass('booking-duplicate-dir col-auto pl-md-3 pl-sm-2 d-flex align-items-center')
            .html('<i class="far fa-folder fa-fw"></i><i class="far fa-folder-open fa-fw"></i>'),
          duplicates_set[0].elem.find('.booking-material').clone(),
          $('<td>').addClass('d-flex align-items-center col-2 col-md-2').text(total_amounts),
          $('<td>').addClass('d-flex align-items-center col')
            .text(`${duplicates_set.length} ${this._$elem.data('i18n-bookings')}`),
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
      duplicates_set[0].elem.before(duplicate_bar);
      for (let duplicate of duplicates_set) {
        duplicate.elem.addClass('booking-duplicate d-none').removeClass('d-flex');
      }
    }
  }
}
