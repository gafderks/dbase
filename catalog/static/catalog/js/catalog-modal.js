import $ from 'jquery';

$('#catalogModal').on('show.bs.modal', function(event) {
  // try to retrieve catalogUrl from relatedTarget attribute, for Autocomplete initiator
  let catalogUrl = event.relatedTarget.catalogUrl;
  if (catalogUrl === undefined) {
    // retrieve catalog from DOM data attribute
    catalogUrl = $(event.relatedTarget).data('catalog-item');
  }
  const $modal = $(this);
  $.get(catalogUrl, function(data) {
    $modal.find('.modal-body').html($(data));
  });
});
