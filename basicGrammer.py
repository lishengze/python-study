# -*- coding: utf-8 -*-
 
a = '默认编码是ascii'
# print a, len(a)
# for c in a:
#     print c
     
# b = unicode (a, "utf-8")
# print b,len(b)
# for c in b:
#     print c

# 递归函数
def fact(n):
    if n == 1:
        return 1
    else:
        return n * fact(n-1)

print  fact(5)
