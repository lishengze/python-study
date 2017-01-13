$(function () {
    console.log ('This is test!')

    $(':checkbox').each(function() {
        console.log ($(this).attr('id'))
    });

    var selectedNumb = 0;
    var sum_checkbox_id = 'checkbox1'
    $(':checkbox').change(function(){            
        if ($(this).attr('id') === sum_checkbox_id) {
            if ($(this).is(':checked')) {
                $(':checkbox').each(function() {
                    if ($(this).attr('id') !== sum_checkbox_id && !$(this).is(':checked')) {
                        $(this).attr("checked", true);
                        ++selectedNumb;
                        $('#selectNumb').text(selectedNumb + ' 个被选中');
                    }
                });
            } else {
                $(':checkbox').each(function() {
                    if ($(this).attr('id') !== sum_checkbox_id && $(this).is(':checked')) {
                        $(this).attr("checked", false);
                        --selectedNumb;
                        $('#selectNumb').text(selectedNumb + ' 个被选中');
                    }
                });                    
            } 
        } else {
            if ($(this).is(':checked')) {
                ++selectedNumb;
            } else {
                --selectedNumb;
            }
            $('#selectNumb').text(selectedNumb + ' 个被选中');
        } 
    })
});