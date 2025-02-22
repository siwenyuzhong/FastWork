!function () {
    function a(a, b) {
        var c = document.createElement("script");
        c.type = "text/javascript", c.readyState ? c.onreadystatechange = function () {
            ("loaded" == c.readyState || "complete" == c.readyState) && (c.onreadystatechange = null, b())
        } : c.onload = function () {
            b()
        }, c.src = a, document.getElementsByTagName("head")[0].appendChild(c)
    }

    function b() {
        function a() {
            $(".menu .menu-dropdown").css({width: 1000 - c.position().left + "px"})
        }

        function b() {
            var a, b, c = $(".menu-dropdown-sidebar").find("a"), d = $(".item-sub[sidebar-type]");
            return {
                eventBind: function () {
                    this.initStatus();
                    var d = null;
                    c.mouseenter(function () {
                        var c = $(this);
                        c.data("enterTime", (new Date).getTime()), c != b && (d = setTimeout(function () {
                            b.removeClass("active"), c.addClass("active"), b = c;
                            var d = c.attr("sidebar-type"), e = $('.item-sub[sidebar-type="' + d + '"]');
                            a.hide(), e.show(), a = e, c.parents(".menu-dropdown").css({height: e.height() + 20 + "px"})
                        }, 200))
                    }).mouseleave(function () {
                        var a = $(this), b = parseInt(a.data("enterTime") || 0, 10), c = (new Date).getTime();
                        200 >= c - b && d && (clearTimeout(d), d = null)
                    }), $("#J_common_header_menu .menu-dropdown-content").mouseenter(function (a) {
                        d && (clearTimeout(d), d = null)
                    })
                }, initStatus: function () {
                    c.removeClass("active"), d.hide(), a = $(".item-sub[sidebar-type]").eq(0).show(), b = f.eq(0).addClass("active")
                }
            }
        }

        var c = ($("#J_common_header_search_wrap"), $("#J_common_header_menu")), d = $(window).width();
        a(), $(window).resize(function () {
            a(), d = $(window).width()
        });
        var e = null, f = $(".menu-dropdown-sidebar").find("a");
        $(".item-sub[sidebar-type]").eq(0);
        $("#J_common_header_menu .top-menu-item").mouseenter(function () {
            var a, b = null, c = $(this);
            (a = c.data("mouseoutTimer")) && (clearTimeout(a), a = null), c.data("enterTime", (new Date).getTime()), b = setTimeout(function () {
                e && (clearTimeout(e), e = null);
                var a = "true" === c.attr("has-dropdown"), b = c.attr("menu-type");
                if (a) {
                    var d = c.parent().position(), f = c.position(), g = c.find(".menu-dropdown");
                    g.css({left: -(f.left - d.left) + "px"});
                    var h = g.find(".menu-dropdown-inner").height();
                    "product" != b && (h += 47), g.addClass("animate").css({height: h + "px", zIndex: 1})
                }
            }, 200), c.data("mouseoverTimter", b)
        }).mouseleave(function (a) {
            var c = $(this), d = parseInt(c.data("enterTime") || 0, 10), e = (new Date).getTime(),
                f = c.data("mouseoverTimter");
            200 >= e - d && f && (clearTimeout(f), f = null);
            var g = "true" === c.attr("has-dropdown");
            if (g) {
                var h = setTimeout(function () {
                    var a = c.find(".menu-dropdown");
                    a.removeClass("animate").css({
                        height: 0,
                        zIndex: 0
                    }), c.data("showing", !1), b.initStatus(), f && (clearTimeout(f), f = null)
                }, 100);
                c.data("mouseoutTimer", h)
            }
        }), b = b(), b.eventBind()
    }

    function c(a, b, c, d) {
        function e() {
            try {
                new ActiveXObject("ShockwaveFlash.ShockwaveFlash");
                return !0
            } catch (a) {
                try {
                    var b = navigator.plugins["Shockwave Flash"];
                    return void 0 == b ? !1 : !0
                } catch (c) {
                    return !1
                }
            }
        }

        var f;
        d.length && (f = d.attr("activity-url")) && 0 == d.find("a").length && d.append('<a style="opacity: 0;filter: alpha(opacity=0);" href="' + f + '" target="_blank">阿里云</a>'), document.all && $(".activity .link a").css({
            background: "#00a2ca",
            filter: "alpha(opacity=0)"
        });
        var g = $(a).attr("only-home"), h = $(a).attr("flash-src");
        if (e()) {
            var i = '<object style="position:absolute;left:0;right:0;" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=8,0,0,0" width="' + b + '" height="' + c + '"><param name="movie" value="' + h + '"><param name="quality" value="high"><param name="wmode" value="transparent"><param name="scale" value="noscale"><embed src="' + h + '" width="' + b + '" height="' + c + '" scale="noscale" quality="high" pluginspage="http://www.macromedia.com/go/getflashplayer" type="application/x-shockwave-flash" wmode="transparent"></embed></object>',
                j = window.location;
            g ? j.host + j.pathname == "www.aliyun.com/" && $(a).html(i) : $(a).html(i)
        }
    }

    function d(a) {
        a.length && 0 == a.find("a").length && a.append('<a href="http://wanwang.aliyun.com/" style="height: 60px;background:#00a2ca;padding-top:0;right:0px;" target="_blank"><image width="114" height="60" src="//gtms02.alicdn.com/tps/i2/TB1Xy2.IpXXXXcVXpXXAwng6FXX-230-124.png" /></a>')
    }

    function e() {
        $(function () {
            if (0 != $("#J_common_header_menu").length) {
                b();
                var a = $("#J-activity-url");
                "wanwang.aliyun.com" == window.location.hostname ? d(a) : c("#J-ali-activity", 230, 62, a)
            }
        })
    }

    window.jQuery ? e() : a("//g.alicdn.com/aliyun/www-dpl/0.3.32/knight/js/base-all.js", function () {
        e()
    })
}();