def copy_array(ori_array):
    result = []
    for i in range(len(ori_array)):
        result.append(ori_array[i])
    return result

def get_empty_dict(item_name_list, item_value):
    result = {}
    for item_name in item_name_list:
        result[item_name] = item_value
    
    return result