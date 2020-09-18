$(function(){
    $('.btn-number').click(function (e) {
        e.preventDefault();

        console.log('we here')

        fieldName = $(this).attr('data-field');
        typeof =  $(this).attr('data-type');
        var input = $("input[name='"+ fieldName +"']");
        var currentVal = parseInt(input.val());
        if (type == 'minus'){
            if (currentVal > input.attr('min')){
                input
                    .val(currentVal - 1)
                    .change();
            }

         if (parseInt(input.val())== input.attr('min')) {
            $(this).attr('disabled', true);
         }

        } else if (type == 'plus'){
            input
                .val(currentVal + 1)
                 .change();
        }

    });

});

// function statusBox(){
//        jQuery('<div id="loading"> Loading...</div>')
//        .prependTo("#main")
//        .ajaxStart(function(){jQuery(this).show();})
//        .ajaxStop(function(){jQuery(this).hide();})
//    }