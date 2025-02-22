$(document).ready(function() {

    $('#howItWorkCarousel').carousel({
        interval: 5000,
        pause: "false"
    });

    var hiw = $('.how_it_work'),
        offset = hiw.offset();

    var elemSlide = $('#howItWorkCarousel').find('.item.active img'),
        elemSrc = elemSlide.attr('src');

    $('#howItWorkCarousel').on('slide.bs.carousel', function() {
        var elemSlide = $('#howItWorkCarousel').find('.item.active img'),
            elemSrc = elemSlide.attr('src');
        // elemSlide.attr('src', '/img/landing5/slide.jpg');
        setTimeout(function() {
            elemSlide.attr('src', elemSrc);
        },500);
    });

    $(window).scroll(function() {
        clearTimeout($.data(this, 'scrollTimer'));
        $.data(this, 'scrollTimer', setTimeout(function() {
            if ($(document).scrollTop() >= hiw.outerHeight()) {

                elemSlide.attr('src', elemSrc);
                $('#howItWorkCarousel').carousel(0);

                $(window).off('scroll');

                var counter = 0;
                var progressBar;

                function progressBarRun() {
                    progressBar = setInterval(function() {
                        counter += 1;
                        if (counter > 100) clearInterval(progressBar);
                            $(".carousel_progressbar").css("width", counter + "%");
                        }, 50);
                }
                progressBarRun();

                $('#howItWorkCarousel').on('slide.bs.carousel', function () {
                    counter = 0;
                    clearInterval(progressBar);
                    progressBarRun();
                });
            }
        }, 50));
    });



    // youtube
    var src_video = 'https://www.youtube.com/embed/G0uDB9jh2Mg?rel=0&showinfo=0&HD=1&autoplay=1';
    $('#button_video').click(function () {
        $('#venyoo_video_iframe').attr('src', src_video);
    });
    $('#venyoo_video').on('hidden.bs.modal', function () {
        $('#venyoo_video_iframe').removeAttr('src');
    })

    $('.type-it').typeIt({
        speed: 50,
        breakLines: false,
        autoStart: false,
        startDelay: false,
        loop: true
    })
    //.tiType('СѓРІРµР»РёС‡РёС‚ РїСЂРѕРґР°Р¶Рё!')
    .tiType(translate.tiTypeText1)
    .tiPause(3000)
    .tiDelete()
    //.tiType('СѓРІРµР»РёС‡РёС‚ РєРѕРЅРІРµСЂСЃРёСЋ СЃР°Р№С‚Р°!')
    .tiType(translate.tiTypeText2)
    .tiPause(3000)
    .tiDelete()
    //.tiType('СЂР°Р±РѕС‚Р°РµС‚ Р°РІС‚РѕРјР°С‚РёС‡РµСЃРєРё!')
    .tiType(translate.tiTypeText3)
    .tiPause(3000)
    .tiDelete()
    //.tiType('СѓРІРµР»РёС‡РёС‚ РєРѕР»РёС‡РµСЃС‚РІРѕ РєР»РёРµРЅС‚РѕРІ!')
    .tiType(translate.tiTypeText4)
    //.tiPause(3000)
    //.tiDelete()
    //.tiType('РґР»СЏ РІР°С€РµРіРѕ СЃР°Р№С‚Р°!')
    //.tiType(translate.tiTypeText5)
    .tiPause(6000)
    .tiDelete()


    //get tarif steps
    var tarifSteps = null;

    $.ajax({
        url: api_tarif_steps,
        success: function (data)
        {
            tarifSteps = data.tarif;
        },
        async: false
    });

    //get step
    function getStepByLeads (leads, tarifSteps)
    {
        var lastPlan = tarifSteps[Object.keys(tarifSteps).length - 1];
        var currentPlan = [];
        var price = 0;

        if(leads)
        {
            Object.keys(tarifSteps).map(function(index)
            {
                var plan = tarifSteps[index];

                //get plan
                if(plan.start <= leads && plan.end >= leads)
                {
                    currentPlan = plan
                }
            });

            //if leads > plan leads
            if(leads > lastPlan.end)
            {
                currentPlan = lastPlan;
            }

            //total
            if(Object.keys(currentPlan).length > 0)
            {
                var leadPrice = currentPlan.moneyLead;
                if (typeof currentPlan.moneyLead === 'string') {
                    var func = new Function("$numLeads", currentPlan.moneyLead);
                    leadPrice = func(leads);
                }

                return leads * leadPrice;
            }
        }
        return price;
    }

    $('#bootRange').slider({
        formatter: function(value)
        {
            var maxLeads = $('#bootRange').data('slider-max');
            var leadsCheck = value;

            if( leadsCheck >= maxLeads )
            {
                $('.addPlus').removeClass('hide');
                $('.minLeadsScroll').addClass('hide');
                $('.maxLeadsScroll').removeClass('hide');
            }
            else
            {
                $('.addPlus').addClass('hide');
                $('.minLeadsScroll').removeClass('hide');
                $('.maxLeadsScroll').addClass('hide');
            }

            $('.color_img').width($('.slider-selection')[0].style.width);

            var price = getStepByLeads(value, tarifSteps);

            $('.tariffMoney').html(Math.ceil(price));

            return $('#bootRangeValue').text(value);

        }
    });

    $('#bootRange').on('slideStop', function(ev){

    });


});