/**
 * Source: https://github.com/caktus/django-project-template/blob/master/project_name/static/js/csrf_ajax.js
 */
import $ from 'jquery';


// CSRF helper functions taken directly from Django docs
function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/i.test(method));
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    let cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = $.trim(cookie);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(
          cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Setup jQuery ajax calls to handle CSRF
$.ajaxPrefilter(function (options, originalOptions, xhr) {
  let csrftoken;
  if (!csrfSafeMethod(options.type) && !options.crossDomain) {
    // Send the token to same-origin, relative URLs only.
    // Send the token only if the method warrants CSRF protection
    // Using the CSRFToken value acquired earlier
    csrftoken = getCookie('csrftoken');
    xhr.setRequestHeader('X-CSRFToken', csrftoken);
  }
});

