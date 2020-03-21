import Booking from './booking.js';

export default class Game {

  constructor($elem, partOfDay, id, order) {
    this._$elem = $elem;
    this._partOfDay = partOfDay;
    this._partOfDayCode = $elem.data('part-of-day-code');
    this._id = id || $elem.data('id');
    this._order = order || $elem.data('order');

    this._bookings = this._constructBookings();
    Booking.initCreateBookingForm(this);
    this._attachEvents();
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
    this.order = this._$elem.data('order') || this._order;
  }

  get id() {
    return this._id;
  }

  get order() {
    return this._order;
  }

  set order(i) {
    // Requires manually calling sortGames
    this._order = i;
    this._$elem.data('order', i);
  }

  set partOfDayCode(code) {
    if (code !== this._partOfDay.partOfDayCode) {
      // Get a reference to the day
      const day = this._partOfDay.day;
      // Remove the game from the current part of day
      this._partOfDay.removeGame(this);
      // Add the game to the new part of day
      this._partOfDay = day.getPartOfDay(code);
      this._partOfDay.addGame(this);
      this._partOfDayCode = code;
    }
  }

  get elem() {
    return this._$elem;
  }

  _attachEvents() {
    // Attach move method to move buttons
    this._$elem.find('.btn.move-game').click(e => {
      e.preventDefault();
      this.update(e.currentTarget);
    });
    // Attach update method to update button
    this._$elem.find('form.game-form').submit(e => {
      e.preventDefault();
      this.update(e.currentTarget);
    });
    // Card edit button
    this._$elem.find('.btn.edit-game').click(_ => this.toggleForm());
    // Form reset button
    this._$elem.find('form.game-form').on('reset', _ => this.toggleForm());
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
    // Card delete button
    this._$elem.find('.delete-game').click(e => {
      const $modal = $('#deleteGameModal');
      const gameName = this._$elem.find('.game-name').text();
      const confirmationTemplate = $modal.find('.modal-body').data('template');
      $modal.find('.modal-body').html(confirmationTemplate.replace('${name}', gameName));
      $modal.find('.confirm-delete').off().click(_ => this.update(e.currentTarget));
    });
    // Tooltip
    this._$elem.find('[data-toggle="tooltip"]').tooltip();
    // Toggle collapse
    this._$elem.find('.game-name').click(_ => this.toggleCollapse());
  }

  toggleForm() {
    this._$elem.find('.card-header').toggleClass('display-form');
  }

  static initCreateGameForm(day) {
    const $form = day.elem.find('.game-form-create');
    $form.submit(e => {
      e.preventDefault();
      Game.create(e.currentTarget, day);
    });
    return $form;
  }

  static create(trigger, day) {
    const $trigger = $(trigger);
    $.ajax({
      url: $trigger.attr('action') || $trigger.data('action'),
      cache: 'false',
      dataType: 'json',
      type: $trigger.attr('method') || $trigger.data('method'),
      data: $trigger.serialize(),
      success: (data) => {
        if (!(data['success'])) {
          $trigger.replaceWith(data['form_html']);
        } else {
          // Construct new game and add it to the part of day
          const newGame = new Game($(data['game_html']));
          newGame._partOfDay = day.getPartOfDay(newGame._partOfDayCode).addGame(newGame);
          // Reset the form
          $trigger.find('[name=name], [name=location]').val('');
        }
        day.sortGames(data['order']);
        day.updateNavigation(data['nav_html']);
      },
      error: function (jqXHR, textStatus, errorThrown) {
        console.log(textStatus);
        console.log(errorThrown);
      }
    });

  }

  update(trigger) {
    const $trigger = $(trigger);
    $.ajax({
      url: $trigger.attr('action') || $trigger.data('action'),
      cache: 'false',
      dataType: 'json',
      type: $trigger.attr('method') || $trigger.data('method'),
      data: $trigger.serialize(),
      success: (data) => {
        if (!(data['success'])) {
          $trigger.replaceWith(data['form_html']);
        } else {
          if ($trigger.hasClass('game-form-update')) {
            const $newGame = $(data['game_html']);
            this._$elem.replaceWith($newGame);
            this._$elem = $newGame;
            this._populateFromDOM();
            this._attachEvents();
          } else if ($trigger.hasClass('delete-game')) {
            this.delete();
          }
        }
        this._partOfDay.day.updateNavigation(data['nav_html']);
        this._partOfDay.day.sortGames(data['order']);
      },
      error: (jqXHR, textStatus, errorThrown) => {
        console.log(textStatus);
        console.log(errorThrown);
      }
    });
  }

  // eslint-disable-next-line no-unused-vars
  onBookingChanged(booking) {
    // noop
  }

  delete() {
    this._$elem.remove();
    this._partOfDay.removeGame(this);
  }

  allowMove() {
    this._$elem.find('.btn.move-game').removeClass('disabled');
  }

  denyMoveUp() {
    this._$elem.find('.btn.move-game-up').addClass('disabled');
  }

  denyMoveDown() {
    this._$elem.find('.btn.move-game-down').addClass('disabled');
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
}
