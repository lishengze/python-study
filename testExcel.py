from excel import EXCEL


def test_get_secode():
    dirname = "D:/strategy"
    filename = "test.xlsx"
    complete_filename = dirname + '/' + filename
    excelobj = EXCEL(complete_filename)
    # secodelist = excelobj.get_data_bysheet("test1")
    secodelist = excelobj.get_data_byindex()

    print secodelist

if __name__ == "__main__":
    test_get_secode()


