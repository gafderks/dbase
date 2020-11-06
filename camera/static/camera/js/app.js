import 'dbase/app';

import $ from 'jquery';
import 'bootstrap';

import 'dbase/ajax_csrf';

(function() {
  // The width and height of the captured photo. We will set the
  // width to the value defined here, but the height will be
  // calculated based on the aspect ratio of the input stream.

  let display_width = 320;    // We will scale the photo width to this
  let display_height = 0;     // This will be computed based on the input stream

  let stream_width = null;
  let stream_height = null;

  // |streaming| indicates whether or not we're currently streaming
  // video from the camera. Obviously, we start at false.

  let streaming = false;

  // The various HTML elements we need to configure or control. These
  // will be set by the startup() function.

  let video = null;
  let canvas = null;
  let photo = null;
  let startbutton = null;

  let currentMaterial = null;

  function startup() {
    video = $('video')[0];
    canvas = $('canvas')[0];
    photo = $('.photo').find('img')[0];
    startbutton = $('.camera-shutter')[0];

    navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: 'environment',
        width: { ideal: 1920 },
        height: { ideal: 1080 },
      },
      audio: false})
      .then(function(stream) {
        video.srcObject = stream;
        video.play();
      })
      .catch(function(err) {
        console.log('An error occurred: ' + err);
      });

    video.addEventListener('canplay', () => {
      if (!streaming) {
        display_width = $('video').width();
        display_height = video.videoHeight / (video.videoWidth/display_width);

        stream_width = video.videoWidth;
        stream_height = video.videoHeight;

        console.log('display', display_width, display_height);
        console.log('stream', stream_width, stream_height);
      
        // Firefox currently has a bug where the height can't be read from
        // the video, so we will make assumptions if this happens.
        if (isNaN(display_height)) {
          display_height = display_width / (4/3);
        }
      
        canvas.setAttribute('width', stream_width);
        canvas.setAttribute('height', stream_height);
        streaming = true;
      }
    }, false);

    startbutton.addEventListener('click', function(ev){
      takepicture();
      ev.preventDefault();
    }, false);

    $('.camera-back').click(() => {
      showCamera();
    });

    let materials = [];
    $('.material-item').each((i, elem) => {
      const material = {
        $elem: $(elem),
        id: $(elem).data('id'),
        name: $(elem).data('name'),
        idx: i
      };
      materials.push(material);
      $(elem).click(() => {
        setMaterial(material);
      });
    });
    currentMaterial = materials[0];

    function nextMaterial() {
      setMaterial(materials[currentMaterial.idx + 1]);
      showCamera();
    }

    $('.camera-skip').click(() => nextMaterial());

    $('.camera-save').click(() => {
      $.ajax({
        type: 'POST',
        url: '/camera/upload',
        data: { 
          image: canvas.toDataURL('image/png'),
          material: currentMaterial.id
        }
      }).done(() => {
        nextMaterial();
      });

    });

    clearphoto();
  }

  function setMaterial(material) {
    currentMaterial = material;
    $('.camera-material strong').text(material.name);
  }

  // Fill the photo with an indication that none has been
  // captured.

  function clearphoto() {
    const context = canvas.getContext('2d');
    context.fillStyle = '#AAA';
    context.fillRect(0, 0, canvas.width, canvas.height);

    const data = canvas.toDataURL('image/png');
    photo.setAttribute('src', data);
  }
  
  // Capture a photo by fetching the current contents of the video
  // and drawing it into a canvas, then converting that to a PNG
  // format data URL. By drawing it on an offscreen canvas and then
  // drawing that to the screen, we can change its size and/or apply
  // other changes before drawing it.

  function takepicture() {
    const context = canvas.getContext('2d');
    if (stream_width && stream_height) {
      canvas.width = stream_width;
      canvas.height = stream_height;
      context.drawImage(video, 0, 0, stream_width, stream_height);
    
      const data = canvas.toDataURL('image/png');
      photo.setAttribute('src', data);
      showPhoto();
    } else {
      clearphoto();
    }
  }

  function showPhoto() {
    $('.photo').removeClass('d-none');
    $('.camera').addClass('d-none');
  }

  function showCamera() {
    $('.photo').addClass('d-none');
    $('.camera').removeClass('d-none');
  }

  // Set up our event listener to run the startup process
  // once loading is complete.
  window.addEventListener('load', startup, false);
})();
