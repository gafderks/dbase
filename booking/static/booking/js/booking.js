import Autocomplete from './autocomplete.js';

export default class Booking {

  constructor($elem, game, id) {
    this._$elem = $elem;
    this._game = game;
    this._id = id || $elem.data('id');
    this._autocomplete = undefined;
    this._attachEvents();
  }

  get id() {
    return this._id;
  }

  get elem() {
    return this._$elem;
  }

  _attachEvents() {
    // Init Typeahead
    const $bookingForm = this._$elem.find('form.booking-form');
    this._autocomplete = Autocomplete.getAutocomplete($bookingForm.find('.typeahead-materials'));
    // Attach update method to update button
    $bookingForm.submit(e => {
      e.preventDefault();
      this.update(e.currentTarget);
    });
    // Booking edit button
    this._$elem.find('.btn.edit-booking').click(_ => {
      // Reset the value of the typeahead to the initial value
      this._autocomplete.reset();
      this.toggleForm();
    });
    // Form reset button
    $bookingForm.on('reset', _ => this.toggleForm());
    // Bootstrap toggles
    this._$elem.find('[data-toggle=toggle][type=checkbox]').each((i, elem) => {
      $(elem).bootstrapToggle({
        on: $(elem).data('on'),
        off: $(elem).data('off'),
      });
      // FIXME Set the width of the checkbox. https://github.com/gitbrent/bootstrap4-toggle/issues/26#issuecomment-581728024
      $(elem).parent().css({
        height: '2.5rem',
        width: '112px'
      });
    });
    // Booking delete button
    this._$elem.find('.delete-booking').click(e => {
      const $modal = $('#deleteBookingModal');
      const bookingName = this._$elem.find('.booking-material').find('label').text();
      const confirmationTemplate = $modal.find('.modal-body').data('template');
      $modal.find('.modal-body').html(confirmationTemplate.replace('${name}', bookingName));
      $modal.find('.confirm-delete').off().click(_ => {
        this.update(e.currentTarget);
      });
    });
    // Tooltip
    this._$elem.find('[data-toggle="tooltip"]').tooltip();
  }

  toggleForm() {
    this._$elem.toggleClass('display-form');
  }

  update(trigger) {
    const $trigger = $(trigger);
    const form_data = $trigger.serializeArray();
    if (form_data.length) {
      form_data.find(input => input.name === 'material').value = this._autocomplete.selectedItem.id;
    }
    $.ajax({
      url: $trigger.attr('action') || $trigger.data('action'),
      cache: 'false',
      dataType: 'json',
      type: $trigger.attr('method') || $trigger.data('method'),
      data: $.param(form_data),
      success: data => {
        if (!(data['success'])) {
          $trigger.replaceWith(data['form_html']);
        } else {
          if ($trigger.hasClass('booking-form-update')) {
            const $newBooking = $(data['booking_html']);
            this._$elem.replaceWith($newBooking);
            this._$elem = $newBooking;
            this._attachEvents();
          } else if ($trigger.hasClass('delete-booking')) {
            this.delete();
          }
        }
      },
      error: (jqXHR, textStatus, errorThrown) => {
        console.log(textStatus);
        console.log(errorThrown);
      }
    });
  }

  static create(trigger, game) {
    const $trigger = $(trigger);
    const form_data = $trigger.serializeArray();
    const autocomplete = Autocomplete.getAutocomplete($trigger.find('.typeahead-materials'));
    form_data.find(input => input.name === 'material').value = autocomplete.selectedItem.id;
    $.ajax({
      url: $trigger.attr('action') || $trigger.data('action'),
      cache: 'false',
      dataType: 'json',
      type: $trigger.attr('method') || $trigger.data('method'),
      data: $.param(form_data),
      success: (data) => {
        if (!(data['success'])) {
          $trigger.replaceWith(data['form_html']);
        } else {
          // Construct new booking and add it to the game
          const newBooking = new Booking($(data['booking_html']), game);
          game.addBooking(newBooking);
          // Reset the form
          $trigger.find('[name=amount], [name=workweek], [name=comment]').val('');
          autocomplete.reset();
        }
      },
      error: function (jqXHR, textStatus, errorThrown) {
        console.log(textStatus);
        console.log(errorThrown);
      }
    });
  }

  static initCreateBookingForm(game) {
    const $form = game.elem.find('.booking-form-create');
    Autocomplete.getAutocomplete($form.find('.typeahead-materials'));
    $form.submit(e => {
      e.preventDefault();
      Booking.create(e.currentTarget, game);
    });
    return $form;
  }

  delete() {
    this._$elem.remove();
    this._game.removeBooking(this);
  }


}
