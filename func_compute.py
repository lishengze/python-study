import math

def compare_restore_close(data_list_a, data_list_b, max_error=0.0000):
    result = []
    for code_name in data_list_a:
        date = data_list_a[code_name][0]    
        if code_name in data_list_b: 
            delta = math.fabs((float(data_list_a[code_name][2]) - float(data_list_b[code_name][2])) 
                              / float(data_list_b[code_name][2]))
            if delta > max_error:
                result.append([code_name, \
                               data_list_a[code_name][3], data_list_a[code_name][0], data_list_a[code_name][2], \
                               data_list_b[code_name][3], data_list_b[code_name][0], data_list_b[code_name][2], 
                               delta])
    return result

def get_ave(ori_data):
    result = 0
    for item in ori_data:
        result += float(item)
    result /= len(ori_data)
    return result

def get_ave_dev(ori_data):
    result = 0
    ave_value = get_ave(ori_data)
    for data in ori_data:
        result += float(math.fabs(data-ave_value))
    result /= len(ori_data)
    return result

def rebound(ori_data, max_value, min_value):
    result = ori_data
    if ori_data > max_value:
        result = max_value

    if ori_data < min_value:
        result = min_value

    return result