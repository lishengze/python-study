$(function () {
    console.log ('This is class Test!')

    var selectedNumb = 0;
    var sum_checkbox_id = 'action-toggle'
  	var setNumbSelector = $('.paginator')
  	var testCheckbox = 0;
    $(':checkbox').change(function(){
		    // console.log(++testCheckbox);
        if ($(this).attr('id') === sum_checkbox_id) {
            if ($(this).is(':checked')) {
                $('.action-select').each(function() {
                    if (!$(this).is(':checked')) {
                    // if ($(this).attr('checked') !== 'checked') {
						// console.log('Is action-toggle checked!')
						// console.log ('')
                        $(this).attr("checked", true);
                        ++selectedNumb;
                        setNumbSelector.text(selectedNumb + ' 个被选中');
                    }
                });
            } else {
                $('.action-select').each(function() {
                    if ($(this).is(':checked')) {
						// console.log('Is action-toggle unchecked!')
						// console.log ('')
                        $(this).attr("checked", false);
                        --selectedNumb;
                        setNumbSelector.text(selectedNumb + ' 个被选中');
                    }
                });
            }

            $('.action-select').each(function() {
                // console.log ($(this).attr('checked'));
                // console.log ($(this).is(':checked'));
            })
        } else {
            if ($(this).is(':checked')) {
                ++selectedNumb;
                $(this).attr("checked", true);
            } else {
                --selectedNumb;
                $(this).attr("checked", false);
            }
            setNumbSelector.text(selectedNumb + ' 个被选中');

            $('.action-select').each(function() {
                // console.log ($(this).attr('checked'));
                // console.log ($(this).is(':checked'));
            })
        }
    })

    $('.hrefJump').click(function(){
        url = '/admin.html/'
        group_name = $(this).text();
        console.log(group_name);
        $.ajax({
          url: '/AJAX/Set_Chosen_Group/',
          data: {'req_json': group_name},
          dataType: 'json',
          type: 'POST',
          traditional: true,
          success: function (responseJSON) {
              console.log (responseJSON)
              if (responseJSON.error !== '') {
                alert(responseJSON.error)
              } else {
                window.location.href = responseJSON.data;
              }
          }
        });
        // window.location.href = url;
    })

    $("#execute_selection").click(function(){
        // console.log($("select option:selected").attr('value'))
        // console.log($("select option:selected").text())
        if ($("select option:selected").attr('value') === "delete_selected") {
            // console.log($("select option:selected").text());
            var delete_group = [];
            $(":checked").each(function(){
                group_name = $(this).parent().parent().find(".hrefJump").text()
                // console.log(group_name)
                delete_group.push(group_name)
            })

            delete_group.shift();
            console.log (delete_group)

            $.ajax({
                url: '/AJAX/Delete_Group/',
                data: {'delete_group': delete_group},
                dataType: 'json',
                type: 'POST',
                traditional: true,
                success: function (responseJSON) {
                    console.log (responseJSON)
                }
            });
        }
        // return false
    })

    $("input[value='保存']").click(function(){
      var group_name = $("#id_name").val();
      var group_group = '';

      $("#id_permissions_to").find("option").each(function(){
          group_group += $(this).text() + ";"
      })

      if (group_group === '') {
        alert('还没选择组群权限!')
      } else {
        var req_data = {
          'name': group_name,
          'permission':group_group,
        }
        console.log (req_data)
        $.ajax({
          url: '/AJAX/Add_Group/',
          data: {'req_data': JSON.stringify(req_data)},
          dataType: 'json',
          type: 'POST',
          traditional: true,
          success: function (responseJSON) {
              console.log (responseJSON)
              if (responseJSON.status === "Successful") {
                window.location.href = '/admin/auth/group';
              } else {
                alert('添加组群失败!');
              }
          }
        });
      }
      return false;
    })

    $("#id_permissions_from").find("option").click(function(event){
      // 激活Choose图标, 改变样式.
      if (!event.ctrlKey) {
        $("#id_permissions_from").find("option").each(function(){
            $(this).attr('selected', false);
        })
      }else {
        console.log ('Control Key!')
      }

      $(this).attr('selected', true);

      $("#id_permissions_from").find("option").each(function(){
          if ($(this).attr('selected')) {
              console.log ($(this).attr('title'));
          }
      })
    })

    $("#id_permissions_to").find("option").click(function(event){
      // 激活Choose图标, 改变样式.
      if (!event.ctrlKey) {
        $("#id_permissions_to").find("option").each(function(){
            $(this).attr('selected', false);
        })
      }else {
        console.log ('Control Key!')
      }

      $(this).attr('selected', true);

      $("#id_permissions_to").find("option").each(function(){
          if ($(this).attr('selected')) {
              console.log ($(this).attr('title'));
          }
      })
    })

    $("#id_permissions_add_link").click(function(){
      // 添加选中的权限
      $("#id_permissions_from").find("option").each(function(){
          if ($(this).attr('selected')) {
              console.log ($(this).attr('title'));
              var html_element = '<option value="'+ $(this).attr('value') +'" title="'+ $(this).attr('title') +'"> '+ $(this).text() +' </option>'
              $("#id_permissions_to").append(html_element);
          }
      })
    })

    $("#id_permissions_remove_link").click(function(){
      // 移除选中的权限
      $("#id_permissions_to").find("option").each(function(){
          if ($(this).attr('selected')) {
              $(this).remove()
          }
      })
    })

});
