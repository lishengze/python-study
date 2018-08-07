def print_data(msg, data):
    print ("\n", msg, len(data))
    if len(data) > 50:
        data = data[0:50]

    for item in data:
        print (item)

def print_dict_data(msg, data):
    print('\n')
    print (msg, len(data))
    for item in data:
        print (item,": ", data[item])
    print('\n')

def print_list(msg, data, numb=50):
    print ('\n')
    print (msg, len(data))
    # if len(data) > numb:
    #     data = data[0:numb]

    for item in data:
        print (item)

    print ('\n')
