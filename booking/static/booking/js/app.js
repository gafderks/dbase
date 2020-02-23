function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

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
