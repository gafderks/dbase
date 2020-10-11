import 'dbase/app';

import 'dbase/autocomplete';
import Day from './day.js';

$('.day').each((i, elem) => {
  $(elem).data('day', new Day($(elem)));
});

$(window).on('activate.bs.scrollspy', (e, obj) => {
  const activeDay = $(obj.relatedTarget).data('day');
  if (activeDay !== undefined) {
    $('.card-header-pills a').removeClass('active');
    $(`.card-header-pills a[href="#day${activeDay}"]`).addClass('active');
  }
});

$(function () {
  $('[data-toggle="tooltip"]').tooltip();
});
