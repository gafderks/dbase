/*global Game */

class Day {

    constructor($elem, date, evnt, group) {
        this._$elem = $elem;
        this._date = date || $elem.data('date');
        const $booking = $('#booking');
        this._evnt = evnt || $booking.data('event');
        this._group = group || $booking.data('group');

        this._partOfDays = this._constructPartOfDays();
    Game.initCreateGameForm(this);
  }

  get elem() {
    return this._$elem;
  }

    sortGames(order) {
      for (const partOfDay of this._partOfDays) {
        partOfDay.sortGames(order);
      }
    }

    _constructPartOfDays() {
        let partOfDays = [];
        this._$elem.find('.part-of-day').each((i, elem) => {
           const pod = new PartOfDay($(elem), this);
           $(elem).data('part-of-day', pod);
           partOfDays.push(pod)
        });
        return partOfDays;
    }



}


$('.day').each((i, elem) => {
    $(elem).data('day', new Day($(elem)));
});
