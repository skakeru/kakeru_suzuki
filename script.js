$(function(){



  // キーワード説明hover
  $('.keyword').hover(
    function() {
      $(this).find('.hover-contents').addClass('hover-active');

    },
    function() {
      $(this).find('.hover-contents').removeClass('hover-active');

    }
  );


// header段増やし(top)
  $("#button-for-top").hover(
    function() {
      $(".header-item-top-hide").css('display','block');//ONマウス時の背景色
       },
    function() {
      $(".header-item-top-hide").css('display','none');//OFFマウス時
              });

  $(".headers-item-top-hide").hover(
    function() {
      $(".header-item-top-hide").css('display','block');//ONマウス時の背景色
       },
    function() {
      $(".header-item-top-hide").css('display','none');//OFFマウス時
              });

// header段増やし(photo)
  $("#button-for-photo").hover(
  function() {
    $(".header-item-photo-hide").css('display','block');//ONマウス時の背景色
     },
  function() {
    $(".header-item-photo-hide").css('display','none');//OFFマウス時
            });

  $(".headers-item-photo-hide").hover(
  function() {
    $(".header-item-photo-hide").css('display','block');//ONマウス時の背景色
     },
  function() {
    $(".header-item-photo-hide").css('display','none');//OFFマウス時
            });

  // header段増やし(portfolio)
  $("#button-for-portfolio").hover(
  function() {
    $(".header-item-portfolio-hide").css('display','block');//ONマウス時の背景色
     },
  function() {
    $(".header-item-portfolio-hide").css('display','none');//OFFマウス時
            });

  $(".headers-item-portfolio-hide").hover(
  function() {
    $(".header-item-portfolio-hide").css('display','block');//ONマウス時の背景色
     },
  function() {
    $(".header-item-portfolio-hide").css('display','none');//OFFマウス時
            });





// header色変化(top)
 $(".header-item-top").hover(
   function() {
     $(this).css('color','white');//ONマウス時の背景色
      },
   function() {
     $(this).css('color','black');//OFFマウス時
             });

$(".header-item-top").hover(
  function() {
    $('header').css('background','black');//ONマウス時の背景色
      },
  function() {
    $('header').css('background','white');//OFFマウス時
            });

$(".header-item-top").hover(
  function() {
    $('.header-item-top').css('background','black');//ONマウス時の背景色
      },
  function() {
    $('.header-item-top').css('background','white');//OFFマウス時
            });

// header色変化(photo)
$(".header-item-photo").hover(
  function() {
    $(this).css('color','#273464');//ONマウス時の背景色
     },
  function() {
    $(this).css('color','white');//OFFマウス時
            });

$(".header-item-photo").hover(
 function() {
   $('.header-photo').css('background','white');//ONマウス時の背景色
     },
 function() {
   $('.header-photo').css('background','#273464');//OFFマウス時
           });

$(".header-item-photo").hover(
  function() {
   $(".header-item-photo").css('background','white');//ONマウス時の背景色
     },
  function() {
   $(".header-item-photo").css('background','#273464');//OFFマウス時
           });

// header色変化(portfolio)
 $(".header-item-portfolio").hover(
   function() {
     $(this).css('color','#7C0001');//ONマウス時の背景色
      },
   function() {
     $(this).css('color','white');//OFFマウス時
             });

$(".header-item-portfolio").hover(
  function() {
    $('.header-portfolio').css('background','white');//ONマウス時の背景色
      },
  function() {
    $('.header-portfolio').css('background','#7C0001');//OFFマウス時
            });

$(".header-item-portfolio").hover(
  function() {
   $(".header-item-portfolio").css('background','white');//ONマウス時の背景色
     },
  function() {
   $(".header-item-portfolio").css('background','#7C0001');//OFFマウス時
           });





// SNSボタン(色変え)上
$('#insta-mark').hover(
  function(){
    $(this).children('span').css('color','#CF2E92');
  },
  function(){
    $(this).children('span').css('color','black');
  }
);

$('#facebook-mark').hover(
  function(){
    $(this).children('span').css('color','#3C5A99');
  },
  function(){
    $(this).children('span').css('color','black');
  }
);

$('#twitter-mark').hover(
  function(){
    $(this).children('span').css('color','#1DA1F2');
  },
  function(){
    $(this).children('span').css('color','black');
  }
);





// SNSボタン(色変え)下
$('#insta-icon').hover(
  function(){
    $(this).children('span').css('color','#CF2E92');
  },
  function(){
    $(this).children('span').css('color','black');
  }
);



$('#facebook-icon').hover(
  function(){
    $(this).children('span').css('color','#3C5A99');
  },
  function(){
    $(this).children('span').css('color','black');
  }
);

$('#twitter-icon').hover(
  function(){
    $(this).children('span').css('color','#1DA1F2');
  },
  function(){
    $(this).children('span').css('color','black');
  }
);



// ページ内リンク(photo)


const scrollTop_cycling_tour_club = $('#cycling-tour-club').offset().top;

$('#button-for-cycling-tour-club').click(function(){
   $('html,body').animate({
     'scrollTop':scrollTop_cycling_tour_club
   },1000);
  });



const scrollTop_studying_english_in_malta = $('#studying-english-in-malta').offset().top;

$('#button-for-studying-english-in-malta').click(function(){
   $('html,body').animate({
     'scrollTop':scrollTop_studying_english_in_malta
   },1000);
  });

const scrollTop_backpacker = $('#backpacker').offset().top;

$('#button-for-backpacker').click(function(){
   $('html,body').animate({
     'scrollTop':scrollTop_backpacker
   },1000);
  });













});
