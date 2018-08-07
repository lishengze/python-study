def compute_netvalue(ori_data):
    result = []
    index = 0
    pre_value = 1
    while index < len(ori_data):
        curr_value = pre_value * (1 + ori_data[index])
        result.append(curr_value)
        pre_value = curr_value
        index += 1
    return result
    
def compute_retrancemnet(ori_data):
    max_value = 0
    result = []
    index = 0
    while index < len(ori_data):
        data = ori_data[index]
        if data > max_value:
            max_value = data
        result.append(data / max_value - 1)
        index += 1
    return result
