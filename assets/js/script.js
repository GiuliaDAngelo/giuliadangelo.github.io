// Preloader

function PageLoad() {
  $("body").removeClass("hidden");
  TweenMax.to($(".preloader-text"), 1, {
    force3D: true,
    opacity: 1,
    y: 0,
    delay: 0.2,
    ease: Power3.easeOut,
  });

  var width = 100,
    perfData = window.performance.timing,
    EstimatedTime = -(perfData.loadEventEnd - perfData.navigationStart),
    time = parseInt((EstimatedTime / 500) % 50) * 70;

  // Percentage Increment Animation
  var PercentageID = $("#precent"),
    start = 1,
    end = 100,
    durataion = time;
  animateValue(PercentageID, start, end, durataion);

  function animateValue(id, start, end, duration) {
    var range = end - start,
      current = start,
      increment = end > start ? 1 : -1,
      stepTime = Math.abs(Math.floor(duration / range)),
      obj = $(id);

    var timer = setInterval(function () {
      current += increment;
      $(obj).text(current);
      if (current === end) {
        clearInterval(timer);
      }
    }, stepTime);
  }
  // Fading Out Loadbar on Finised
  setTimeout(function () {
    TweenMax.to($(".percentage, .inner"), 0.7, {
      force3D: true,
      opacity: 0,
      yPercent: -101,
      ease: Power3.easeInOut,
    });
    TweenMax.to($(".preloader-wrap"), 0.7, {
      force3D: true,
      yPercent: -150,
      delay: 0.2,
      ease: Power3.easeInOut,
    });
  }, time);
}
$(document).ready(function () {
  // preloder
  PageLoad();

  // change-navigation-color
  $(window).scroll(function () {
    if ($(document).scrollTop() > 200) {
      $(".navbar").addClass("nav__color__change");
    } else {
      $(".navbar").removeClass("nav__color__change");
    }
  });

  // Smooth scrolling
  var scrollLink = $(".scroll");
  scrollLink.click(function (e) {
    let elem = $(this.hash);
    if (elem.length) {
      e.preventDefault();
      $("body,html").animate(
        {
          scrollTop: elem.offset().top,
        },
        1000
      );
    }
  });

  $(".navbar-nav>li>a").on("click", function () {
    $(".navbar-collapse").collapse("hide");
  });

  // expertise slider
  $(".expertise__slider").slick({
    infinite: false,
    slidesToShow: 3,
    slidesToScroll: 1,
    dots: false,
    arrows: false,
    responsive: [
      {
        breakpoint: 992,
        settings: {
          slidesToShow: 2,
          slidesToScroll: 1,
          dots: true,
        },
      },
      {
        breakpoint: 768,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1,
          dots: true,
        },
      },
    ],
  });

  // Prevent page jump on resume tab change
  var scrollPosition = 0;
  $('.resume a[data-toggle="tab"]').on('show.bs.tab', function () {
    scrollPosition = $(window).scrollTop();
  });
  $('.resume a[data-toggle="tab"]').on('shown.bs.tab', function () {
    $(window).scrollTop(scrollPosition);
  });

  // skill count
  $(".skill__progress").waypoint(
    function () {
      $(".progress-value span").each(function () {
        $(this)
          .prop("Counter", 0)
          .animate(
            {
              Counter: $(this).text(),
            },
            {
              duration: 3000,
              easing: "swing",
              step: function (now) {
                $(this).text(Math.ceil(now));
              },
            }
          );
      });
      this.destroy();
    },
    {
      offset: "80%",
    }
  );

  // venobox
  $(".venobox").venobox();

  // mixitup
  var mixer = mixitup(".portfolio__item__wrapper");

  // testimonial slider
  $(".testimonial__slider").slick({
    infinite: true,
    slidesToShow: 2,
    slidesToScroll: 1,
    dots: true,
    arrows: false,
    responsive: [
      {
        breakpoint: 992,
        settings: {
          slidesToShow: 2,
          slidesToScroll: 1,
        },
      },
      {
        breakpoint: 768,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1,
        },
      },
    ],
  });

  // clients slider
  $(".clients__slider").slick({
    infinite: true,
    slidesToShow: 5,
    slidesToScroll: 1,
    dots: false,
    arrows: false,
    responsive: [
      {
        breakpoint: 992,
        settings: {
          slidesToShow: 3,
          slidesToScroll: 1,
        },
      },
      {
        breakpoint: 768,
        settings: {
          slidesToShow: 2,
          slidesToScroll: 1,
        },
      },
      {
        breakpoint: 480,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1,
        },
      },
    ],
  });

  // contact form
  $("#contact-form").on("submit", function (e) {
    e.preventDefault();
    $.ajax({
      url: "contact.php",
      type: "POST",
      data: $("#contact-form").serialize(),
      success: function (data) {
        $("#contact-form").each(function () {
          this.reset();
        });
      },
    });
  });

  // wow js
  new WOW().init();

  // headroom
  $(".navbar").headroom();
});

// Preloader
function PageLoad() {
  if ($("#preloader").length) {
    $("#preloader")
      .delay(100)
      .fadeOut("slow", function () {
        $(this).remove();
      });
  }
}
