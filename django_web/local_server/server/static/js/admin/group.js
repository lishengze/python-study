$(function () {
    console.log ('This is group!')

    $(':checkbox').each(function() {
        console.log ($(this).attr('class'))
    });

    var selectedNumb = 0;
    var sum_checkbox_id = 'action-toggle'
    var set_numb_class = 'paginator'
    $(':checkbox').change(function(){            
        if ($(this).attr('id') === sum_checkbox_id) {
            if ($(this).is(':checked')) {
                $(':checkbox').each(function() {
                    if ($(this).attr('id') !== sum_checkbox_id && !$(this).is(':checked')) {
                        $(this).attr("checked", true);
                        ++selectedNumb;
                        $('.' + set_numb_class).text(selectedNumb + ' 个被选中');
                    }
                });
            } else {
                $(':checkbox').each(function() {
                    if ($(this).attr('id') !== sum_checkbox_id && $(this).is(':checked')) {
                        $(this).attr("checked", false);
                        --selectedNumb;
                        $('.' + set_numb_class).text(selectedNumb + ' 个被选中');
                    }
                });                    
            } 
        } else {
            if ($(this).is(':checked')) {
                ++selectedNumb;
            } else {
                --selectedNumb;
            }
            $('.' + set_numb_class).text(selectedNumb + ' 个被选中');
        } 
    })
});