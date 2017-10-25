# str = "\u9a71\u52a8\u7a0b\u5e8f\u7ba1\u7406\u5668 \u5728\u6307\u5b9a\u7684 DSN \u4e2d\uff0c\u9a71\u52a8\u7a0b\u5e8f\u548c\u5e94\u7528\u7a0b\u5e8f\u4e4b\u95f4\u7684\u4f53\u7cfb\u7ed3\u6784\u4e0d\u5339\u914d"
# str = "\u8bed\u53e5\u6bb5\u7f3a\u5c11\u7ed3\u675f \x00\x00\x00\xb0\x00\x00\x00\x00\x00\x00\x00 \u5601\u06b4\x00\x00\u1bce\uecb1\u07fe\x00\u0f01\u0667\x00\x00\u7a00\u03c6\x00\x00O\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\u7d18\uecb9\u07fe\x00\ube80\u06b5\x00\x00\ubee0\u06b5\x00\x00P\x00\x00\x00\x00\x00\x00\x00\ufffe\uffff "
str = ["\x00\x00\u0492\u1d37\x00\x00\ua238\u0226\x00\x00\x06", 
       "\u955a\n\u7d9e"
    #    "\u5601\u1bce\uecb1\u07fe\x00\u0f01\u0667\x00\x00\u7a00\u03c6",
    #    "\x00\x00O\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00",
    #    "\ubee0\u06b5\x00\x00P\x00\x00\x00\x00\x00\x00\x00\ufffe\uffff",
       ]
for data in str:        
    data = data.decode('unicode_escape')
    print data

