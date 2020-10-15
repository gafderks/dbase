import $ from 'jquery';

$('#catalogModal').on('show.bs.modal', function(event) {
  const $button = $(event.relatedTarget);
  const catalogUrl = $button.data('catalog-item');
  const $modal = $(this);
  $.get(catalogUrl, function(data) {
    $modal.find('.modal-body').html($(data));
  });
});
