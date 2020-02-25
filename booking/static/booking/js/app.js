import Day from './day.js';

$('.day').each((i, elem) => {
  $(elem).data('day', new Day($(elem)));
});
