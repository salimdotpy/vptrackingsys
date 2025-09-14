$(window).ready(function () {
  $('.loading').fadeOut('slow');
});

// ========================================================================================================
// Don't tamper my touchable carousel(Image slider) function
$(function () {
  const carousels = $('.carousel');
  carousels.each(function (i) {
    const element = $(this);
    element.carousel();
    element.find('.left').click(function () {
      element.carousel('prev');
    });
    element.find('.right').click(function () {
      element.carousel('next');
    });
    element.touchStartX = element.touchEndX = 0;
    element.distance = 100;
    element.handleTS = function (event) {
      if (event.touches && event.touches.length > 0)
        element.touchStartX = event.touches[0].clientX;
    };
    element.handleTM = function (event) {
      element.touchEndX = 0;
      if (event.touches && event.touches.length > 0)
        element.touchEndX = event.touches[0].clientX;
    };
    element.handleTE = function (event) {
      let space = element.touchEndX - element.touchStartX;
      if (space > element.distance) element.carousel('prev');
      else if (space < -element.distance) element.carousel('next');
    };
    element.ce = document.getElementsByClassName('carousel')[i];
    element.ce.addEventListener('touchstart', element.handleTS);
    element.ce.addEventListener('touchmove', element.handleTM);
    element.ce.addEventListener('touchend', element.handleTE);
  });
});
// ========================================================================================================

// ========================================================================================================
// Don't tamper my toast(short-time message) function
const toast = function () {
  const tm = this;
  this.con =
    $('.notifications').length === 0
      ? $('<ul class="notifications"></ul>').insertAfter($('body'))
      : $('.notifications');
  this.default = {
    timer: 5000,
    pos: 'top-right',
    success: {
      icon: 'fa-check-circle',
      text: 'Success: This is a success toast.',
    },
    error: { icon: 'fa-times-circle', text: 'Error: This is an error toast.' },
    warning: {
      icon: 'fa-exclamation-triangle',
      text: 'Warning: This is a warning toast.',
    },
    info: {
      icon: 'fa-info-circle',
      text: 'Info: This is an information toast.',
    },
  };
  this.applyPos = function (toast) {
    let pos = toast.pos;
    if (pos == 'top-left')
      $(toast)
        .parent()
        .css('top', '60px')
        .css('bottom', '')
        .css('right', '')
        .css('transform', '')
        .css('left', '0');
    else if (pos == 'top-center')
      $(toast)
        .parent()
        .css('top', '60px')
        .css('left', '50%')
        .css('bottom', '')
        .css('right', '')
        .css('transform', 'translateX(-50%)');
    else if (pos == 'bottom-right')
      $(toast)
        .parent()
        .css('bottom', '20px')
        .css('right', '0')
        .css('top', '')
        .css('left', '')
        .css('transform', '');
    else if (pos == 'bottom-left')
      $(toast)
        .parent()
        .css('bottom', '20px')
        .css('left', '0')
        .css('top', '')
        .css('right', '')
        .css('transform', '');
    else if (pos == 'bottom-center')
      $(toast)
        .parent()
        .css('bottom', '20px')
        .css('left', '50%')
        .css('top', '')
        .css('right', '')
        .css('transform', 'translateX(-50%)');
    else if (pos == 'left-center')
      $(toast)
        .parent()
        .css('top', '50%')
        .css('left', '0')
        .css('bottom', '')
        .css('right', '')
        .css('transform', 'translateY(-50%)');
    else if (pos == 'right-center')
      $(toast)
        .parent()
        .css('top', '50%')
        .css('right', '0')
        .css('bottom', '')
        .css('left', '')
        .css('transform', 'translateY(-50%)');
    else if (pos == 'middle')
      $(toast)
        .parent()
        .css('top', '50%')
        .css('left', '50%')
        .css('bottom', '')
        .css('right', '')
        .css('transform', 'translateX(-50%) translateY(-50%)');
    else
      $(toast)
        .parent()
        .css('top', '60px')
        .css('right', '0')
        .css('bottom', '')
        .css('left', '')
        .css('transform', 'none');
  };
  this.removeToast = function (toast) {
    toast.addClass('hide-toast');
    if (toast.timeoutId) clearTimeout(toast.timeoutId);
    setTimeout(function () {
      toast.remove();
    }, 1000);
  };
  this.createToast = function (options) {
    let key = ['success', 'error', 'warning', 'info'];
    this.option = typeof options == 'object' && options ? options : tm.default;
    let id = key[Math.floor(Math.random() * 4)];
    let text = this.option.text || tm.default[id].text,
      icon = this.option.icon || id;
    let toast = document.createElement('li');
    toast.className = 'mytoast ' + icon;
    toast.innerHTML =
      '<div class="column"> ' +
      '<i class="fa ' +
      this.default[icon].icon +
      '"></i> ' +
      '<span>' +
      text +
      '</span> ' +
      '<i class="fa fa-times close" onclick="new toast().removeToast($(this).parent().parent())"></i>' +
      '<div class="indicator"></div></div> ';
    tm.con.append(toast);
    let timer = this.option.timer || tm.default.timer;
    $(toast)
      .find('.indicator')
      .animate({ width: 0 }, timer, 'linear', 'forwards');
    toast.pos = this.option.pos == undefined ? tm.default.pos : this.option.pos;
    tm.con.children().length <= 1 ? tm.applyPos(toast) : '';
    if (tm.con.children().length <= 1) {
      if (['top-left', 'bottom-left', 'left-center'].includes(toast.pos))
        $(toast).addClass('toast-l');
      else if (
        ['top-right', 'bottom-right', 'right-center'].includes(toast.pos)
      )
        $(toast).addClass('toast-r');
      else $(toast).addClass('toast-m');
    } else $(toast).addClass($(toast).prev().attr('class').split(' ')[2]);
    toast.timeoutId = setTimeout(function () {
      tm.removeToast($(toast));
    }, timer);
    $(toast).hover(
      function (ev) {
        clearTimeout(toast.timeoutId);
        $(toast)
          .find('.indicator')
          .animate()
          .stop()
          .width(100 + '%');
      },
      function () {
        $(toast)
          .find('.indicator')
          .animate({ width: 0 }, timer, 'linear', 'forwards');
        toast.timeoutId = setTimeout(function () {
          tm.removeToast($(toast));
        }, timer);
      }
    );
  };
};
function toast_it(option) {
  const toasts = new toast();
  toasts.createToast(option);
}

// ================================================================================

$('#toggle').on('click', function (e) {
  if (e.target !== document.querySelectorAll('.fa-bars')[0]) return;
  $('body').toggleClass('open');
  $('.collapse').removeClass('in');
});
$('#mobile').on('click', function (e) {
  if (e.target !== document.querySelectorAll('.fa-bars')[1]) return;
  $('body').toggleClass('mobile-open');
  $('.side-flow').css('display', 'block').animate({ left: '0' }, 10);
  $('aside').css('display', 'block').animate({ left: '0' }, 30);
});
$(window).on('click', function (e) {
  if (e.target == document.getElementById('aside')) {
    let s = $('aside'),
      a = $('.side-flow');
    $('body').addClass('mobile-open');
    a.css('display', 'block').animate({ left: -a.width() - 15 }, 10);
    s.css('display', 'block').animate({ left: -s.width() - 15 }, 10);
  }
});
$(document).on('mouseenter mouseleave', '.side-nav li', function (ev) {
  let body = $('body');
  let sidebarIconOnly = body.hasClass('open');
  if (!('ontouchstart' in document.documentElement)) {
    if (sidebarIconOnly) {
      let $menuItem = $(this),
        link = $menuItem.children().first(),
        sub = $menuItem.find('.collapse');
      if (ev.type === 'mouseenter') {
        link.hasClass('dropdown')
          ? sub.addClass('in').css('height', 'auto')
          : sub.removeClass('in');
        $menuItem.addClass('hover-open');
        link.removeClass('collapsed');
      } else {
        $menuItem.removeClass('hover-open');
        sub.removeClass('in');
        link.addClass('collapsed');
      }
    }
  }
});

let cord_pos,
  loc_pos = { lat: 7.7200717, lng: 4.41305 };
//Get location function
function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.watchPosition(showPosition, showError, {
      enableHighAccuracy: true,
      maximumAge: 5000,
    });
  } else {
    toast_it({
      text: 'Geolocation is not supported by this browser.',
      icon: 'error',
    });
  }
}

function showPosition(position) {
  loc_pos = position
    ? { lat: position.coords.latitude, lng: position.coords.longitude }
    : { lat: 6.1334096, lng: 6.8075828 };
  $('[name="latitude"]').val(loc_pos.lat);
  $('[name="longitude"]').val(loc_pos.lng);
}
function showError(error) {
  let x = '';
  switch (error.code) {
    case error.PERMISSION_DENIED:
      x = 'User denied the request for Geolocation.';
      break;
    case error.POSITION_UNAVAILABLE:
      x = 'Location information is unavailable.';
      break;
    case error.TIMEOUT:
      x = 'The request to get user location timed out.';
      break;
    case error.UNKNOWN_ERROR:
      x = 'An unknown error occurred.';
      break;
  }
  toast_it({ text: x, icon: 'warning' });
  loc_pos = { lat: 6.1334096, lng: 6.8075828 };
}

function generateQRCode(eleId = 'qrcode', text = 'test') {
  const ele = document.getElementById(eleId);
  ele.innerHTML = '';
  new QRCode(ele, {
    text: text,
    width: 128,
    height: 128,
  });
}

function downloadQRcode(eleId = 'qrcode', filename = 'qrcode.png') {
  let qrElement = document.querySelector(`#${eleId}`);
  if (!qrElement) {
    toast_it({ text: 'QR Code not generated yet.', icon: 'error' });
    return;
  }

  domtoimage
    .toPng(qrElement)
    .then(function (dataUrl) {
      const link = document.createElement('a');
      link.href = dataUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast_it({ text: 'Downloaded Successfully', icon: 'success' });
    })
    .catch(function () {
      // fallback: try canvas with white padding + border
      let canvasEl = document.querySelector(`#${eleId} canvas`);
      if (!canvasEl) throw new Error('Canvas not found');

      $(canvasEl).addClass('p-4 bg-white border border-success');

      return domtoimage
        .toPng(canvasEl)
        .then(function (dataUrl) {
          const link = document.createElement('a');
          link.href = dataUrl;
          link.download = filename;
          document.body.appendChild(link);
          link.click();
          link.remove();

          toast_it({ text: 'Downloaded Successfully', icon: 'success' });
        })
        .catch(function (error) {
          console.error('oops, something went wrong!', error);
          toast_it({ text: 'oops, something went wrong!', icon: 'error' });
        })
        .finally(function () {
          // always clean up classes
          $(canvasEl).removeClass('p-4 bg-white border border-success');
        });
    });
}

function addGarage(e) {
  const garageCon = `
    <div class="col-md-6">
        <div class="input-group">
            <input type="text" class="form-control" placeholder="Enter garage name" name="garages[]" />
            <button class="btn btn-danger" type="button" title="Remove garage" onclick="removeGarage(this)">
                <i class="fa fa-times-circle"></i>
            </button>
        </div>
    </div>`;
  $(e).parent().before(garageCon);
}

function removeGarage(e) {
  $(e).parent().parent().remove();
}

const tooltipTriggerList = document.querySelectorAll(
  '[data-bs-toggle="tooltip"], [data-bs-toggle1="tooltip"]'
);

const tooltipList = [...tooltipTriggerList].map(
  (tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl)
);

async function getLocation2() {
  return new Promise((resolve, reject) => {
    if (navigator.geolocation) {
      navigator.geolocation.watchPosition(
        (position) => {
          cord_pos = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };
          resolve(cord_pos);
        },
        (error) => {
          let errorMessage = '';
          switch (error.code) {
            case error.PERMISSION_DENIED:
              errorMessage = 'User denied the request for Geolocation.';
              break;
            case error.POSITION_UNAVAILABLE:
              errorMessage = 'Location information is unavailable.';
              break;
            case error.TIMEOUT:
              errorMessage = 'The request to get user location timed out.';
              break;
            case error.UNKNOWN_ERROR:
              errorMessage = 'An unknown error occurred.';
              break;
          }
          console.error(errorMessage);
          toast_it({ text: errorMessage, icon: 'warning' });
          cord_pos = { lat: 7.733841, lng: 4.421263 }; // Fallback coordinates
          resolve(cord_pos);
        },
        { enableHighAccuracy: true, maximumAge: 5000 }
      );
    } else {
      console.error('Geolocation is not supported by this browser.');
      cord_pos = { lat: 7.733841, lng: 4.421263 }; // Fallback coordinates
      toast_it({
        text: 'Geolocation is not supported by this browser.',
        icon: 'error',
      });
      resolve(cord_pos);
    }
  });
}
