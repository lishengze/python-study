def testWriteFile():
    resultFileName = "secodeResult.txt"
    wfile = open(resultFileName,'w')
    rstStr = "SecodeInfo numb is  : " + str(len([1,2,3]))
    wfile.write(rstStr)    

    rstStr = "\nSum count is " + str(10) + '\n'
    print rstStr
    wfile.write(rstStr)
    wfile.close()