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
}).on('hidden.bs.modal', function() {
  // remove the material card from the modal and show the loading spinner again
  const $modal = $(this);
  $modal.find('.modal-body').html(`<div class="d-flex justify-content-center">
      <div class="spinner-grow text-secondary m-5" role="status">
        <span class="sr-only">${$modal.data('loading')}</span>
      </div>
    </div>`);
});
