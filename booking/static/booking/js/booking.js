import $ from 'jquery';
import 'popper.js';
import 'bootstrap';
import 'bootstrap4-toggle';
import Autocomplete from 'dbase/autocomplete';

export default class Booking {

  constructor($elem, container, id) {
    this._$elem = $elem;
    this._container = container; // BookingContainer
    this._id = id || $elem.data('id');
    this._autocomplete = undefined;
    this._$checkbox = this._$elem.find('.booking-check input');
    this._attachEvents();
  }

  get id() {
    return this._id;
  }

  get elem() {
    return this._$elem;
  }

  get material_id() {
    return this._$elem.data('material-id');
  }

  get material_name() {
    return this._$elem.data('material-name');
  }

  get game_id() {
    return this._$elem.data('game-id');
  }

  get group_id() {
    return this._$elem.find('[data-group-id]').data('group-id');
  }

  get amount() {
    return this._$elem.data('amount');
  }

  get stock() {
    return this._$elem.data('stock');
  }

  get checkboxStatus() {
    if (this._$checkbox.prop('indeterminate')) {
      return 'indeterminate';
    } else {
      return this._$checkbox.prop('checked');
    }
  }

  set checkboxStatus(status) {
    if (status === null) {
      // nothing
      return;
    } else if (status === 'true' || status === true) {
      this._$checkbox.prop('checked', true);
      this._$checkbox.prop('indeterminate', false);
    } else if (status === 'false' || status === false) {
      this._$checkbox.prop('checked', false);
      this._$checkbox.prop('indeterminate', false);
    } else if (status === 'indeterminate') {
      this._$checkbox.prop('indeterminate', true);
    } else {
      console.error('Unsupported status');
    }
    this._save_checkbox_status(status);
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
    this._$elem.find('.btn.edit-booking').click(() => {
      // Reset the value of the typeahead to the initial value
      this._autocomplete.reset();
      this.toggleForm();
    });
    // Form reset button
    $bookingForm.on('reset', () => this.toggleForm());
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
      $modal.find('.confirm-delete').off().click(() => {
        this.update(e.currentTarget);
      });
    });
    // Tooltip
    this._$elem.find('[data-toggle="tooltip"]').tooltip();
    // Checkboxes retrieve status
    this._retrieve_checkbox_status();
    // Checkbox indeterminate on double click
    this._$elem.find('.booking-check label').bind('dblclick', () => {
      window.getSelection().removeAllRanges(); // Remove accidental text selection
      this._$checkbox.prop('indeterminate', true);
      this._save_checkbox_status('indeterminate');
      this._container.onBookingCheckboxChanged();
    });
    this._$elem.find('.booking-check input').change(() => {
      this._save_checkbox_status(this._$checkbox.prop('checked'));
      this._container.onBookingCheckboxChanged();
    });
  }

  toggleForm() {
    this._$elem.toggleClass('display-form');
  }

  update(trigger) {
    const $trigger = $(trigger);
    const form_data = $trigger.serializeArray();
    if (form_data.length) {
      if (this._autocomplete.selectedItem.id === this._autocomplete.selectedItem.name) {
        // Custom item
        form_data.find(input => input.name === 'material').value = '';
        form_data.find(input => input.name === 'custom_material').value = this._autocomplete.selectedItem.name;
      } else {
        // Set the material to the selected item
        form_data.find(input => input.name === 'material').value = this._autocomplete.selectedItem.id;
        form_data.find(input => input.name === 'custom_material').value = '';
      }
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
            this._container.onBookingChanged(this);
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
    if (form_data.length) {
      if (autocomplete.selectedItem.id === autocomplete.selectedItem.name) {
        // Custom item
        form_data.find(input => input.name === 'material').value = '';
        form_data.find(input => input.name === 'custom_material').value = autocomplete.selectedItem.name;
      } else {
        // Set the material to the selected item
        form_data.find(input => input.name === 'material').value = autocomplete.selectedItem.id;
        form_data.find(input => input.name === 'custom_material').value = '';
      }
    }
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
          // Move cursor to the material field
          $trigger.find('.typeahead-materials').focus();
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

  _retrieve_checkbox_status() {
    this.checkboxStatus = window.localStorage.getItem(this._$checkbox.attr('id'));
  }

  _save_checkbox_status(status) {
    window.localStorage.setItem(this._$checkbox.attr('id'), status);
  }

  delete() {
    this._$elem.remove();
    this._container.removeBooking(this);
  }


}
