$(document).ready(function() {
    /*$($('.wrapper')[0]).on('click', function() {
        $('#entrance-block').addClass('move');
        $('#home').addClass('move');
        $($('#entrance-block.move')[0]).on('animationend', function() {
            $('#entrance-block').css({
                'display': 'none'
            });
        });  // 메인 에니메이션 취소
    });*/

    $('.card').on('click', function(e) {
        $(e.target).parent().addClass('card-move');
        $(e.target).parent().on('animationend', function(e) {
            $(e.target).removeClass('card-move');
            getForm($($(e.target).children()[1]).children()[1].value);
        });
    });

    function getForm(value) {
        var form = document.createElement('form');
        var request = document.createElement('input');
     
        form.method = 'GET';
        form.action = 'about_me/';
     
        request.type = 'hidden';
        request.name = 'pk';
        request.value = value;
     
        form.appendChild(request);
        document.body.appendChild(form);

        form.submit();
    }
});