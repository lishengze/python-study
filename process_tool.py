from subprocess import check_output
# from subprocess import Popen
import os

def get_process_id_list(process_name):
    # cmd_rst = os.system('tasklist')
    # status, cmd_rst = commands.getstatusoutput("ls")  
    cmd_rst = os.popen('tasklist').readlines()
    # cmd_rst = os.system('tasklist')
    rst_list = cmd_rst.split('\n')
    print(rst_list)
    result = []
    # for item in rst_list:
    #     if process_name in item:
    #         tmp_list = item.split(' ')
    #         if ' ' in tmp_list:
    #             tmp_list.remove(' ')
    #         result.append(tmp_list[1])
        
    # print(result)
    return result


def get_pid(name):
    return map(int,check_output(["pidof",name]).split())

def get_deltea_process_id_list(old_list, new_list):
    pass

def kill_id_list(id_list):
    pass



def test_get_process_id_list():
    # print (get_pid('python'))
    print (get_process_id_list('python'))

if __name__ == "__main__":
    test_get_process_id_list()