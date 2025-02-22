$(document).ready(function() {

	function headerFixed() {
        if ($(document).scrollTop() > 1) {
            $('.main .v_header').removeClass('landing_header');
        } else {
            $('.main .v_header').addClass('landing_header')
        }
    }

    function headerAddFixed() {
        if ($(document).scrollTop() > 1) {
            $('.v_header').addClass('fixed');
        } else {
            $('.v_header').removeClass('fixed');
        }
    }

    headerFixed();

    $(document).scroll(function() {
        headerFixed();
        headerAddFixed();
    });

    $('.button_menu').on('click', function() {
        $('.v_menu').addClass('active');
    });

    $('.close_menu_button').on('click', function() {
        $('.v_menu').removeClass('active');
    });
    $('.v_menu_a').on('click', function() {
        $('.v_menu').removeClass('active');
    });
    if($(window).width()>768){
        $('.autofocus').focus();
    }

    $('[data-toggle="tooltip"]').tooltip();

    function scrollToBlock(btn) {
        $('html, body').animate({
            scrollTop: btn.offset().top - $('.v_header').height()
        }, 300);
    }

    $("[href*='#landing-rate-scroll']").on('click',function() {
        scrollToBlock($(".landing-rate-scroll"));
    });

    if(window.location.hash == '#landing-rate-scroll'){
        scrollToBlock($(".landing-rate-scroll"));
    }

    $("[href*='#integration_block']").on('click',function() {
        scrollToBlock($(".landing-integration-scroll"));
    });

    if(window.location.hash == '#integration_block'){
        scrollToBlock($(".landing-integration-scroll"));
    }

    $("[href*='#mob_app_block']").on('click',function() {
        scrollToBlock($(".landing-mob-app-scroll"));
    });

    if(window.location.hash == '#mob_app_block'){
        scrollToBlock($(".landing-mob-app-scroll"));
    }

    function yearlyCheck() {
        $('.package_picker').toggleClass('yearly');
        $('.adv_tables').toggleClass('yearly');
        console.log('12313')
        if ($('.switcher').checked) {
            console.log('fefefe')
        }
    }

    $('.switcher').on('click', yearlyCheck)

    $("#howItWorkCarousel").swiperight(function() {
        $(this).carousel('prev');
    });
    $("#howItWorkCarousel").swipeleft(function() {
        $(this).carousel('next');
    });

    $("#capabilitiesCarousel").swiperight(function() {
        $(this).carousel('prev');
    });
    $("#capabilitiesCarousel").swipeleft(function() {
        $(this).carousel('next');
    });

});