import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def draw_pic(x_data, y_data, x_label):
    plt.figure(0)
    plt.plot(x_data, y_data, label='Annualized_Returns')
    plt.xlabel(x_label)
    plt.ylabel('Annualized_Returns')
    plt.show()

def testParams():
    # A
    x_data = [0.002863195, \
                0.002863957, \
                0.002857983, \
                0.002854882, \
                0.00285066, \
                0.002840418, \
                0.002845297, \
                0.002869107, \
                0.002885727, \
                0.002911553, \
                0.00294583, \
                0.002978882, \
                0.003019656, \
                0.003086735, \
                0.003154284, \
                0.003258775, \
                0.003405264, \
                0.003599283, \
                0.003840572, \
                0.004133306
                ]

    y_data = [0.073113852, \
            0.073227267, \
            0.073765984, \
            0.071390679, \
            0.06642352, \
            0.068006608, \
            0.068357652, \
            0.061745432, \
            0.060381662, \
            0.07688191, \
            0.075824138, \
            0.072548218, \
            0.073927681, \
            0.085325072, \
            0.085786366, \
            0.09456711, \
            0.083397577, \
            0.049231809, \
            0.074502512, \
            0.089948283]
    x_label = "A"   
    draw_pic(x_data, y_data, x_label)  

def test_trade_today_improve():
    # A
    x_data = [-0.01, -0.03, -0.05, -0.07, -0.09,  \
            -0.11, -0.13, -0.15, -0.17, -0.19, \
            -0.21, -0.23, -0.25, -0.27, -0.29, \
            -0.31, -0.33, -0.35, -0.37, -0.39,\
            -0.41, -0.43, -0.45, -0.47, -0.49, \
            -0.51, -0.53, -0.55, -0.57, -0.59, \
            -0.61, -0.63, -0.65, -0.67, -0.69, \
            -0.71, -0.73, -0.75, -0.77, -0.79]
    # y_data = [0.073113852, \
    #             0.073227267, \
    #             0.073765984, \
    #             0.071390679, \
    #             0.06642352, \
    #             0.068006608, \
    #             0.068357652, \
    #             0.061745432, \
    #             0.060381662, \
    #             0.07688191, \
    #             0.075824138, \
    #             0.072548218, \
    #             0.073927681, \
    #             0.085325072, \
    #             0.085786366, \
    #             0.09456711, \
    #             0.083397577, \
    #             0.049231809, \
    #             0.074502512, \
    #             0.089948283, \
    #             0.093112073, \
    #             0.094005102, \
    #             0.094733627, \
    #             0.099649528, \
    #             0.100189148, \
    #             0.112508907, \
    #             0.090080191, \
    #             0.092679411, \
    #             0.069578444, \
    #             0.060509142, \
    #             0.044912083, \
    #             0.025578352, \
    #             0.021113012, \
    #             0.07372268, \
    #             0.0325516, \
    #             0.026943252, \
    #             0.007153351, \
    #             0.005797071, \
    #             -0.038730482, \
    #             -0.039171877]   
    y_data = [-0.041231288, \
                -0.040857641, \
                -0.039840591, \
                -0.041540338, \
                -0.045926771, \
                -0.046882094, \
                -0.047211987, \
                -0.053193188, \
                -0.053530065, \
                -0.040978262, \
                -0.048436335, \
                -0.057004857, \
                -0.057351229, \
                -0.047309601, \
                -0.040536266, \
                -0.032928844, \
                -0.041505409, \
                -0.035300238, \
                -0.048789276, \
                -0.07724636, \
                -0.065000438, \
                -0.05807365, \
                -0.058119607, \
                0.034878814, \
                0.120086445, \
                0.175195407, \
                0.077243676, \
                0.111223168, \
                0.103458913, \
                0.117786714, \
                0.184448085, \
                0.146568543, \
                0.171949961, \
                0.142713217, \
                0.034770189, \
                0.009767508, \
                0.017658473, \
                0.038132882, \
                0.029822928, \
                0.049265311
                ]
    x_label = "A"  

    # 涨跌停持仓比:

    # # B
    # x_data = [0.01, 0.03, 0.05, 0.07, 0.09,  \
    #             0.11, 0.13, 0.15, 0.17, 0.19, \
    #             0.21, 0.23, 0.25, 0.27, 0.29, \
    #             0.31, 0.33, 0.35, 0.37, 0.39]
    # y_data = [-0.039840591, \
    #             -0.06919477, \
    #             -0.075915858, \
    #             -0.075136521, \
    #             -0.071295792, \
    #             -0.093248071, \
    #             -0.11224643, \
    #             -0.132641222, \
    #             -0.145485311, \
    #             -0.160666382, \
    #             -0.175960471, \
    #             -0.188254408, \
    #             -0.205606051, \
    #             -0.214361959, \
    #             -0.216448167, \
    #             -0.22160011, \
    #             -0.225988853, \
    #             -0.223328851, \
    #             -0.237558689, \
    #             -0.243291719]
    # x_label = "B"  
    
    # # C
    x_data = [-0.01, -0.03, -0.05, -0.07, -0.09,  \
                -0.11, -0.13, -0.15, -0.17, -0.19, \
                -0.21, -0.23, -0.25, -0.27, -0.29, \
                -0.31, -0.33, -0.35, -0.37, -0.39]
    # y_data = [-0.327436616, \
    #         -0.212602076, \
    #         -0.137181631, \
    #         -0.081798174, \
    #         -0.039840591, \
    #         -0.010016464, \
    #         0.009699771, \
    #         0.024748379, \
    #         0.035256688, \
    #         0.043359405, \
    #         0.049832245, \
    #         0.055812858, \
    #         0.061075588, \
    #         0.066558013, \
    #         0.070193891, \
    #         0.072159357, \
    #         0.072590052, \
    #         0.072646196, \
    #         0.073354911, \
    #         0.073765984
    #         ]   

    y_data = [0.25637431, \
                0.285812384, \
                0.251087876, \
                0.21806666, \
                0.184448085, \
                0.131638362, \
                0.086365331, \
                0.086994159, \
                0.089512582, \
                0.050473999, \
                0.044434316, \
                -0.004558862, \
                0.018981658, \
                0.012988955, \
                -0.010953258, \
                -0.042169414, \
                -0.0606857, \
                0.008748758, \
                0.012679369, \
                0.044912083]   
    x_label = "C"  
    draw_pic(x_data, y_data, x_label)    

def test_trade_today():
    x_data = [-0.01, -0.02, -0.03, -0.04,-0.05,\
                        -0.06, -0.07, -0.08, -0.09]
    y_data = [0.072376873,\
                0.072402742,\
                0.072534173,\
                0.070225354,\
                0.07073595,\
                0.065312304,\
                0.062782582,\
                0.05459681,\
                0.051716438
                ]
    x_label = 'A'

    x_data = [0.01, 0.03, 0.05, 0.07, 0.09,  \
                0.11, 0.13, 0.15, 0.17, 0.19, \
                0.21, 0.23, 0.25, 0.27, 0.29, \
                0.31, 0.33, 0.35, 0.37, 0.39, \
                0.41, 0.43, 0.45, 0.47, 0.49, \
                0.51, 0.53, 0.55, 0.57, 0.59, \
                0.61, 0.63, 0.65, 0.67, 0.69, \
                0.71, 0.73, 0.75, 0.77, 0.79]
    y_data = [0.072534173, \
                0.066772963, \
                0.06089379, \
                0.057164244, \
                0.054123533, \
                0.048305996, \
                0.044452594, \
                0.042381496, \
                0.039453412, \
                0.033023012, \
                0.028314483, \
                0.025177304, \
                0.023315593, \
                0.019116074, \
                0.021444988, \
                0.024852639, \
                0.023647646, \
                0.022325624, \
                0.015007842, \
                0.031788088, \
                0.022824697, \
                0.022202152, \
                0.017050024, \
                0.007088443, \
                -0.006563423, \
                -0.008665632, \
                -0.012372769, \
                -0.01537885, \
                -0.014840704, \
                -0.014483255, \
                -0.022428813, \
                -0.021337052, \
                -0.023622798, \
                -0.026173833, \
                -0.028261828, \
                -0.030544168, \
                -0.033123786, \
                -0.031575275, \
                -0.030283834, \
                -0.035246469
                ]
    x_label = 'B'

    # x_data = [-0.01, -0.03, -0.05, -0.07, -0.09,  \
    #             -0.11, -0.13, -0.15, -0.17, -0.19, \
    #             -0.21, -0.23, -0.25, -0.27, -0.29, \
    #             -0.31, -0.33, -0.35, -0.37, -0.39]   
    # y_data = [-0.316935878, \
    #             -0.233960275, \
    #             -0.148480215, \
    #             -0.086937836, \
    #             -0.040844313, \
    #             -0.008457785, \
    #             0.010192323, \
    #             0.025428776, \
    #             0.034905112, \
    #             0.043015735, \
    #             0.049524499, \
    #             0.055786221, \
    #             0.06082965, \
    #             0.066459035, \
    #             0.069361164, \
    #             0.071572891, \
    #             0.071442664, \
    #             0.071657334, \
    #             0.072132834, \
    #             0.072534173
    #         ]
    # x_label = 'C'     

    draw_pic(x_data, y_data, x_label)   


if __name__ =='__main__':
    # main()
    # test_trade_today()
    test_trade_today_improve()