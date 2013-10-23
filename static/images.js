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

    var popup = document.createElement( 'div' );
    popup.style.position = 'fixed';
    popup.style.height = '100%';
    popup.style.width = '100%';
    popup.style.left = '0px';
    popup.style.top = '0px';
    popup.style.zIndex = '999';
    popup.style.overflow = 'auto';
    popup.style.textAlign = 'center';
    popup.style.backgroundColor = 'rgba(0,0,0,0.3)';
    popup.style.cursor = 'pointer';
    document.body.style.overflow = 'hidden';

    popup.onmousedown = function () {
        return false;
    };
    popup.onclick = function () {
        document.body.style.overflow = 'auto';
        this.parentNode.removeChild( this );
        $('div.video').css('visibility','visible');
    };

    popup.appendChild( img );

    document.body.appendChild( popup );
}


function showSmall( img, offset ) {
    var popup = document.createElement( 'div' );
    popup.style.border = '1px solid black';
    popup.style.position = 'absolute';
    popup.style.top = offset.top + 'px';
    popup.style.left = offset.left + 'px';
    popup.style.cursor = 'pointer';
    //popup.style.boxShadow = '0px 0px 8px #000';
    popup.onclick = function () {
        this.parentNode.removeChild( this );
        $('div.video').css('visibility','visible');
    };

    popup.appendChild( img );

    document.body.appendChild( popup );
}

function img_on_click(img, src)
{
    var $overlay = $(img).parent().children('#overlay');
    $overlay.show();
    var im = document.createElement( 'img' );
    im.src = src;

    $(im).load(function () {
        $('div.video').css('visibility','hidden');
        $overlay.hide();
        if ( this.height > screenSize().height || this.width > screenSize().width ) {
            showBig( this );
        }
        else {
            showSmall( this, getOffsetSum( img ) );
        }
    });
    im.onerror = function () {
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
    };

    return false;
}