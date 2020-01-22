const $game_form = $('#game-form')[0];
const $booking = $('#booking');

function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function assignRandomIds(form) {
    // Assigns random ids to all elements that have a name and an id defined.
    // Label for attributes are updated as well.
    $(form).find("[name][id]").each(function(j, elem) {
        const old_id = $(elem).attr('id');
        const new_id = uuidv4();
        $(elem).attr('id', new_id);
        $(form).find("[for=" + old_id + "]").each(function(k, elem) {
           $(elem).attr('for', new_id);
        });
    });
    return form;
}

$days = $('.day');

$days.each(function(i, day) {
    // Create a game form for each day
    let form = document.importNode($game_form.content, true);
    // Assign random ids to avoid clashes with other forms
    form = assignRandomIds(form);
    // Set the hidden values
    let $form = $(form);
    let $day = $(day);
    $form.find('[name=event]').attr('value', $booking.data('event'));
    $form.find('[name=day]').attr('value', $(day).data('date'));
    $form.find('[name=group]').attr('value', $booking.data('group'));
    // Remove the CSRF token
    $form.find('[name=csrfmiddlewaretoken]').remove();
    $card = $('<div class="card editor new-game d-print-none"><div class="card-header"></div></div>');
    $card.find('.card-header').append(form);
    $day.append($card);
});

$days.on('submit', '.game-form', function(e) {
    e.preventDefault();
    updateGame(e.currentTarget);
});

$days.on('reset', '.game-form', function(e) {
    $(e.currentTarget).closest('.card-header').removeClass('display-form');
});

$days.on('click', '.btn.edit-game', function(e) {
   $(e.currentTarget).closest('.card-header').addClass('display-form');
});
$days.on('click', '.btn.move-game', function(e) {
   e.preventDefault();
   updateGame(e.currentTarget);
});

$('#deleteGameModal').on('show.bs.modal', function(e) {
   const $game = $(e.relatedTarget).closest('.game');
   const $modal = $(this);
   const gameName = $game.find('.game-name').text();
   const confirmationTemplate = $modal.find('.modal-body').data('template');
   $modal.find('.modal-body').html(confirmationTemplate.replace('${name}', gameName));
   //$modal.find('.confirm-delete').data('action', $(e.relatedTarget).data('action')).data('method', $(e.relatedTarget).data('method'));
   $modal.find('.confirm-delete').click(function(f) {
      updateGame(e.relatedTarget);
   });
});

sortGames([]);

function sortGames(order) {
    // Update the order data fields
    for ([the_id, the_order] of order) {
        $(`.game[data-id=${the_id}]`).data('order', the_order);
    }
    $('.part-of-day').each(function() {
        // Sort the games in the document
        $(this).find('.game').sort(function(a, b) {
            return $(a).data('order') - $(b).data('order');
        }).appendTo($(this));
        // Disable appropriate buttons
        $(this).find('.btn.move-game').removeClass('disabled');
        $(this).find('.game').first().find('.btn.move-game-up').addClass('disabled');
        $(this).find('.game').last().find('.btn.move-game-down').addClass('disabled');
    });
}

function updateGame(trigger) {
    const $trigger = $(trigger);
    $.ajax({
      url: $trigger.attr('action') || $trigger.data('action'),
      cache: 'false',
      dataType: 'json',
      type: $trigger.attr('method') || $trigger.data('method'),
      data: $trigger.serialize(),
      beforeSend: function(xhr) {
        xhr.setRequestHeader('X-CSRFToken', csrftoken)
      },
      success: function(data) {
          if (!(data['success'])) {
              $trigger.replaceWith(data['form_html']);
          } else {
              if ($trigger.hasClass('game-form-update')) {
                  let $new_card = $(data['game_html']);
                  $trigger.closest('.card.game').replaceWith($new_card);
                  const $form = $new_card.find('form');
                  if ($form.closest('.part-of-day').data('part-of-day') !== $form.find('[name=part_of_day]').val()) {
                      let $new_part_of_day = $new_card.closest('.day').find(".part-of-day[data-part-of-day='"+ $form.find('[name=part_of_day]').val()  +"']");
                      $new_card.detach().appendTo($new_part_of_day);
                  }
              } else if ($trigger.hasClass('game-form-create')) {
                  let $new_card = $(data['game_html']);
                  const $form = $new_card.find('form');
                  if ($form.closest('.part-of-day').data('part-of-day') !== $form.find('[name=part_of_day]').val()) {
                      let $new_part_of_day = $trigger.closest('.day').find(".part-of-day[data-part-of-day='"+ $form.find('[name=part_of_day]').val()  +"']");
                      $new_card.appendTo($new_part_of_day);
                  }
                  $trigger.find('[name=name], [name=location]').val("");
              } else if ($trigger.hasClass('delete-game')) {
                  $trigger.closest('.game').remove();
              }
          }
          sortGames(data['order']);
      },
      error: function(jqXHR, textStatus, errorThrown) {
          console.log(textStatus);
          console.log(errorThrown);
      }
    });
}
