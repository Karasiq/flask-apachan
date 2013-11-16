function screenSize() {
    var w, h; // Объявляем переменные, w - длина, h - высота
    w = (window.innerWidth
        ? window.innerWidth
        : (document.documentElement.clientWidth
        ? document.documentElement.clientWidth
        : document.body.offsetWidth));
    h = (window.innerHeight
        ? window.innerHeight
        : (document.documentElement.clientHeight
        ? document.documentElement.clientHeight
        : document.body.offsetHeight));
    return {width:w, height:h};
}

function getOffsetSum( elem ) {
    var top = 0, left = 0;
    while ( elem ) {
        top = top + parseFloat( elem.offsetTop );
        left = left + parseFloat( elem.offsetLeft );
        elem = elem.offsetParent
    }

    return {top:Math.round( top ), left:Math.round( left )}
}

function showBig( img ) {

    if ( img.width > screenSize().width ) {
        img.width = screenSize().width - 60;
    }

    document.body.style.overflow = 'hidden';
    $(document.createElement( 'div' ))
        .addClass('zoomed zoomed-big')
        .click(function () {
            document.body.style.overflow = 'auto';
            $(this).remove();
            $('div.video').css('visibility','visible');
        })
        .append(img)
        .appendTo($('body'))
        .animate({opacity:1}, 'fast');
}


function showSmall( img, offset ) {
    $(document.createElement( 'div' ))
        .addClass('zoomed zoomed-small')
        .css('top', offset.top)
        .css('left', offset.left)
        .append(img)
        .appendTo($('body'))
        .animate({opacity:1}, 'fast').click('img', function() {
            $(this).remove();
            $('div.video').css('visibility','visible');
        });
}

function img_on_click(img, src)
{
    var $overlay = $(img).parent().children('#overlay');
    $overlay.show();
    var im = document.createElement( 'img' );
    im.src = src;

    $(im)
        .load(function () {
            $('div.video').css('visibility','hidden');
            $overlay.hide();
            if ( this.height > screenSize().height || this.width > screenSize().width ) {
                showBig( this );
            }
            else {
                showSmall( this, getOffsetSum( img ) );
            }
        })
        .error(function () {
            $overlay.hide();
            this.src = this.src.slice( 0, this.src.lastIndexOf( '.' ) ) + '.png';
            this.onerror = function () {
                this.src = this.src.slice( 0, this.src.lastIndexOf( '.' ) ) + '.gif';
                this.onerror = function () {
                    this.src = this.src.slice( 0, this.src.lastIndexOf( '.' ) ) + '.jpeg';
                    this.onerror = function () {
                        this.src = this.src.slice( 0, this.src.lastIndexOf( '.' ) ) + '.bmp';
                    };
                };
            };
        });

    return false;
}

function enable_image_magnifier() {
    $('a.show-full-image').click('img', function() {
        img_on_click($(this).children("#main")[0], $(this).attr('href'));
        return false;
    });
}