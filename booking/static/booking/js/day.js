import PartOfDay from './partofday.js';
import Game from './game.js';

export default class Day {

  constructor($elem, date, evnt, group) {
    this._$elem = $elem;
    this._date = date || $elem.data('date');
    this._$nav = $elem.find('.day-nav');
    const $booking = $('#booking');
    this._evnt = evnt || $booking.data('event');
    this._group = group || $booking.data('group');

    this._partOfDays = this._constructPartOfDays();
    Game.initCreateGameForm(this);
  }

  get elem() {
    return this._$elem;
  }

  getPartOfDay(code) {
    return this._partOfDays.find(partOfDay => partOfDay.partOfDayCode === code);
  }

  sortGames(order, trigger_game=undefined) {
    for (const partOfDay of this._partOfDays) {
      partOfDay.sortGames(order, trigger_game);
    }
    $('body').scrollspy('refresh');
  }

  updateNavigation(nav) {
    const $nav = $(nav);
    this._$nav.replaceWith($nav);
    this._$nav = $nav;
    $('body').scrollspy('refresh');
  }

  _constructPartOfDays() {
    let partOfDays = [];
    this._$elem.find('.part-of-day').each((i, elem) => {
      const pod = new PartOfDay($(elem), this);
      $(elem).data('part-of-day', pod);
      partOfDays.push(pod);
    });
    return partOfDays;
  }

}
