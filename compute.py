from math import *

class SecodeInfo(object):
    def __init__(price, oriPortfolio, name, time, *weightList):
        self.time = time
        self.name = name
        self.weightList = weightList
        self.price = price
        self.oriPortfolio = oriPortfolio
        self.deltaPortfolio = 0


def computePortfolio(indexPrice, weight, hscount, secodePrice):
    return indexPrice * weight * 300 * hscount / 100 / secodePrice

def test():
    indexPrice = 4018.1
    # secodePrice = 32.18
    # weightList = [2.29578545454545, 2.49562208427563]
    # oriPortfolio = 8300
    # hscountList = [1, 1]

    secodePrice = 51.59
    weightList = [0, 1.01694708179954]
    oriPortfolio = 800
    hscountList = [1, 1]
    
    porfolioSum = 0
    for i in range(len(weightList)):
        porfolioSum = porfolioSum + computePortfolio(indexPrice, weightList[i], hscountList[i], secodePrice)

    porfolioSum = floor(porfolioSum)
    modvalue = porfolioSum % 100
    porfolioSum = porfolioSum - modvalue

    if modvalue > 50:
        porfolioSum = porfolioSum + 100


    print "New Portfolio: ", str(porfolioSum)
    print "Dela Portfolio: ", str(porfolioSum - oriPortfolio)


def testFun(secodeObj, indexPrice, hscountList):
    for i in range(len(secodeObj.weightList)):
        porfolioSum = porfolioSum + computePortfolio(indexPrice, secodeObj.weightList[i], hscountList[i], secodeObj.price)

    porfolioSum = floor(porfolioSum)
    modvalue = porfolioSum % 100
    porfolioSum = porfolioSum - modvalue

    if modvalue > 50:
        porfolioSum = porfolioSum + 100

    secodeObj.deltaPortfolio = porfolioSum - secodeObj.oriPortfolio

    print (secodeObj.name, ", time:", secodeObj.time, ", New Portfolio: ", str(porfolioSum), \
            ", Dela Portfolio: ", str(secodeObj.deltaPortfolio))


def testMain():
    indexPrice = 4018.1
    hscountList = [1, 1]

    secodeObjList = []
    secodeObjList.append(SecodeInfo(price = 32.18, oriPortfolio = 8300, name = "000002", time = "201800305", \
                        [2.29578545454545, 2.49562208427563]))

    secodeObjList.append(SecodeInfo(price = 51.59, oriPortfolio = 800, name = "603858", time = "201800305", \
                       [0, 1.01694708179954]))

    for secodeObj in secodeObjList:
        testFun(secodeObj, indexPrice, hscountList)


def main():
    # test()
    testMain()

if __name__ == "__main__":
    main()