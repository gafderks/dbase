import Game from './game.js';

export default class PartOfDay {

  constructor($elem, day, part_of_day) {
    this._$elem = $elem;
    this._day = day;
    this._date = day._date || $elem.data('date');
    this._part_of_day_code = part_of_day || $elem.data('part-of-day');

    this._games = this._constructGames();
    this.sortGames(); // Sets the correct moving buttons
  }

  _constructGames() {
    let games = [];
    this._$elem.find('.game').each((i, elem) => {
      const game = new Game($(elem), this);
      $(elem).data('game', game);
      games.push(game);
    });
    return games;
  }

  get partOfDayCode() {
    return this._part_of_day_code;
  }

  get day() {
    return this._day;
  }

  addGame(game) {
    this._games.push(game);
    game.elem.appendTo(this._$elem);
    return this;
  }

  removeGame(game) {
    game.elem.detach();
    this._games = this._games.filter(g => g.id !== game.id);
  }

  sortGames(order=undefined) {
    // Assign the new order to each of the game objects
    if (order !== undefined) {
      for (let [game_id, game_order] of order) {
        const game = this._games.find(game => game.id === game_id);
        if (game) {
          game.order = game_order;
        }
      }
    }
    // Sort the games in this._games on the order
    this._games.sort((a, b) => {
      return a.order - b.order;
    });
    // Update the games in the DOM
    for (const [i, game] of this._games.entries()) {
      game.allowMove();
      if (i === 0) {
        game.denyMoveUp();
      }
      if (i === this._games.length - 1) {
        game.denyMoveDown();
      }
      game.elem.appendTo(this._$elem);
    }
  }

}
