import $ from 'jquery';
import 'popper.js';
import 'bootstrap';
import Booking from './booking.js';

export default class BookingContainer {

  constructor($elem, partOfDay) {
    this._$elem = $elem;
    this._partOfDay = partOfDay;
    this._partOfDayCode = $elem.data('part-of-day-code');
    this._bookings = this._constructBookings();
    this._$checkAllCheckbox = this._$elem.find('.check-all input');
    this.onBookingCheckboxChanged();
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
    this._$elem.find('.card-name').click(_ => this.toggleCollapse());
    // Checkbox
    this._$elem.find('.check-all label').bind('dblclick', _ => {
      window.getSelection().removeAllRanges(); // Remove accidental text selection
      this._$checkAllCheckbox.prop('indeterminate', true);
      this._setAllBookingCheckboxes('indeterminate');
    });
    this._$checkAllCheckbox.change(_ => {
      this._setAllBookingCheckboxes(this._$checkAllCheckbox.prop('checked'));
    });
  }

  _setAllBookingCheckboxes(status) {
    for (let booking of this._bookings) {
      booking.checkboxStatus = status;
    }
  }

  // eslint-disable-next-line no-unused-vars
  onBookingChanged(booking) {
    // Expected by Booking items
    // noop
  }

  addBooking(booking) {
    this._bookings.push(booking);
    booking.elem.appendTo(this._$elem.find('.bookings-table').find('tbody'));
    this._$elem.find('.bookings-table thead').removeClass('d-none');
  }

  removeBooking(booking) {
    booking.elem.detach();
    this._bookings = this._bookings.filter(bk => bk.id !== booking.id);
    if (this._bookings.length === 0) {
      this._$elem.find('.bookings-table thead').addClass('d-none');
    }
  }

  onBookingCheckboxChanged() {
    const bookingStatuses = this._bookings.map(booking => booking.checkboxStatus);
    if (bookingStatuses.every(status => status === 'indeterminate')) {
      this._$checkAllCheckbox.prop('indeterminate', true);
    } else if (bookingStatuses.every(status => status === true)) {
      this._$checkAllCheckbox.prop('indeterminate', false);
      this._$checkAllCheckbox.prop('checked', true);
    } else {
      this._$checkAllCheckbox.prop('indeterminate', false);
      this._$checkAllCheckbox.prop('checked', false);
    }
  }

}
