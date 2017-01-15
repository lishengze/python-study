// $(function () {
//     console.log ('This is test!')

//     var selectedNumb = 0;
//     var sum_checkbox_id = 'action-toggle'
// 	var setNumbSelector = $('.paginator')
	
//     $(':checkbox').change(function(){            
//         if ($(this).attr('id') === sum_checkbox_id) {
//             if ($(this).is(':checked')) {
//                 $(':checkbox').each(function() {					 
//                     if ($(this).attr('id') !== sum_checkbox_id && !$(this).is(':checked')) {
//                         $(this).attr("checked", true);
//                         ++selectedNumb;
//                         setNumbSelector.text(selectedNumb + ' 个被选中');
//                     }
//                 });
//             } else {
//                 $(':checkbox').each(function() {
//                     if ($(this).attr('id') !== sum_checkbox_id && $(this).is(':checked')) {
//                         $(this).attr("checked", false);
//                         --selectedNumb;
//                         setNumbSelector.text(selectedNumb + ' 个被选中');
//                     }
//                 });                    
//             } 
//         } else {
//             if ($(this).is(':checked')) {
//                 ++selectedNumb;
//             } else {
//                 --selectedNumb;
//             }
//             setNumbSelector.text(selectedNumb + ' 个被选中');
//         } 
//     })
// });

$(function () {
    console.log ('This is class Test!')

    var selectedNumb = 0;
    var sum_checkbox_id = 'action-toggle'
	var setNumbSelector = $('.paginator')
	var testCheckbox = 0;
    $(':checkbox').change(function(){            
		console.log(++testCheckbox);
        if ($(this).attr('id') === sum_checkbox_id) {
			// console.log('Is action-toggle')
            if ($(this).is(':checked')) {				
                $('.action-select').each(function() {	
					// console.log('Is action-toggle checked!')
                    if (!$(this).is(':checked')) {
						console.log('Is action-toggle checked!')
						console.log ('')
                        $(this).attr("checked", true);
                        ++selectedNumb;
                        setNumbSelector.text(selectedNumb + ' 个被选中');
                    }
                });
            } else {				
                $('.action-select').each(function() {
					// console.log('Is action-toggle unchecked!')
                    if ($(this).is(':checked')) {
						console.log('Is action-toggle unchecked!')
						console.log ('')
                        $(this).attr("checked", false);
                        --selectedNumb;
                        setNumbSelector.text(selectedNumb + ' 个被选中');
                    }
                });                    
            } 
        } else {
            if ($(this).is(':checked')) {
                ++selectedNumb;
            } else {
                --selectedNumb;
            }
            setNumbSelector.text(selectedNumb + ' 个被选中');
        } 
    })
});