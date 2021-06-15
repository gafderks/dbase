import 'dbase/app';

import 'dbase/autocomplete';
import Day from './day.js';
import 'catalog/catalog-modal';
import $ from 'jquery';

$('.day').each((i, elem) => {
  $(elem).data('day', new Day($(elem)));
});

$(window).on('activate.bs.scrollspy', (e, obj) => {
  const activeDay = $(obj.relatedTarget).data('day');
  if (activeDay !== undefined) {
    $('.card-header-pills a').removeClass('active');
    $(`.card-header-pills a[href="#day${activeDay}"]`).addClass('active');
  }
  const activeCard = $(obj.relatedTarget).attr('id');
  if (activeCard !== undefined) {
    const link = $(`.day-nav a[href="#${activeCard}"]`)[0];
    window.setTimeout(() => {
      link.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'start' });
    }, 300);
  }
});

$(function () {
  $('[data-toggle="tooltip"]').tooltip();
});
