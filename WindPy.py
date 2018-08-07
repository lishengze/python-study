# -*- coding: cp936 -*-
"""
?????1.0
???????20130820 ?????????
????????Wind Python??????????WindPy.dll??????
????????
???????Wind??????????
"""

from ctypes import *
import threading
import sys
#import timeit
from datetime import datetime,date,time,timedelta
class c_variant(Structure):
    """
    ??????VC??Variant??????????
    ??????vt(?????c_uint16) ?? c_var_union ?????
    ??????????DLL??????,??POINT(c_variant)??????????free_data????
    """
    _anonymous_ = ("val",)
    pass

class c_safearray_union(Union):
    _fields_=[("pbVal", POINTER(c_byte)),
              ("piVal", POINTER(c_int16)),
              ("plVal", POINTER(c_int32)),
              ("pllVal", POINTER(c_int64)),
              ("pfltVal", POINTER(c_float)),
              ("pdblVal", POINTER(c_double)),
              ("pdate", POINTER(c_double)),              
              ("pbstrVal", POINTER(c_wchar_p)),              
              ("pvarVal", POINTER(c_variant))]

class c_safearraybound( Structure):
    _fields_=[("cElements", c_uint32),
              ("lLbound", c_int32)]

class c_safearray(Structure):
    """
    ??????VC??SafeArray??????????
    """    
    _anonymous_ = ("pvData",)
    _fields_=[("cDims", c_uint16),
              ("fFeatures", c_uint16),
              ("cbElements", c_uint32),
              ("cLocks", c_uint32),
              ("pvData", c_safearray_union),
              ("rgsabound", c_safearraybound*3)]    
class c_tagBRECORD(Structure):
   _fields_=[ ("pvRecord", c_void_p),
              ("pRecInfo", c_void_p)]
 
class c_var_union(Union):
    _fields_=[("llVal", c_int64),
              ("lVal",  c_int32),
              ("bVal",  c_int8),
              ("iVal",  c_int16),
              ("fltVal",c_float),
              ("dblVal",c_double),
              ("date", c_double),
              ("bstrVal", c_wchar_p),
              ("pbVal", POINTER(c_byte)),
              ("piVal", POINTER(c_int16)),
              ("plVal", POINTER(c_int32)),
              ("pllVal", POINTER(c_int64)),
              ("pfltVal", POINTER(c_float)),
              ("pdblVal", POINTER(c_double)),
              ("pdate", POINTER(c_double)),              
              ("pbstrVal", POINTER(c_wchar_p)),
              ("parray", POINTER(c_safearray)),              
              ("pvarVal", POINTER(c_variant)),
              ("__VARIANT_NAME_4",c_tagBRECORD)]          

c_variant._fields_ = [ ("vt",c_uint16), ("wr1",c_uint16),("wr2",c_uint16),("wr3",c_uint16),("val",c_var_union)]

"""
??????VT????
"""  
VT_EMPTY= 0
VT_NULL = 1
VT_I2 = 2
VT_I4 = 3
VT_R4 = 4
VT_R8 = 5
VT_CY = 6
VT_DATE = 7
VT_BSTR = 8
VT_DISPATCH = 9
VT_ERROR  = 10
VT_BOOL = 11
VT_VARIANT  = 12
VT_UNKNOWN  = 13
VT_DECIMAL  = 14
VT_I1 = 16
VT_UI1  = 17
VT_UI2  = 18
VT_UI4  = 19
VT_I8 = 20
VT_UI8  = 21
VT_INT  = 22
VT_UINT = 23

VT_SAFEARRAY  = 27
VT_CF = 71
VT_VECTOR = 0x1000
VT_ARRAY  = 0x2000
VT_BYREF  = 0x4000
VT_RESERVED = 0x8000
VT_ILLEGAL  = 0xffff
VT_ILLEGALMASKED= 0xfff
VT_TYPEMASK = 0xfff

c_StateChangedCallbackType = CFUNCTYPE(c_int32, c_int32, c_int64,c_int32)

gNewDataCome=[3];

gLocker=[threading.Lock()]

gFunctionDict={};
gFuncDictMutex=threading.Lock();
gTradeFunctionDict={};
gTradeFuncMutex=threading.Lock();

class w:
    """
    ??Wind Python????????????????????R??????????????????
    ?????????
    ???????w.start()
    ????????w.wsd,w.wss,w.wst,w.wsi,w.wsq,w.wset,w.wpf,w.tdays,w.tdaysoffset,w.tdayscount???????????
    """

    class c_apiout(Structure):
        """
        ????????API????????????????????????????????????dll????????????????
        """
        #_anonymous_ = ("val",)
        _fields_=[("ErrorCode", c_int32),
                  ("StateCode", c_int32),
                  ("RequestID", c_int64),
                  ("Codes" , c_variant),
                  ("Fields", c_variant),
                  ("Times" , c_variant),
                  ("Data"  , c_variant)]    

        def __str__(self):
            a=".ErrorCode=%d\n"%self.ErrorCode + \
              ".RequestID=%d\n"%self.RequestID 
            return a

        def __format__(self,fmt):
            return str(self);
        def __repr__(self):
            return str(self);
    
    """
    ????WindPy.dll ????
    ??????c_start,c_stop,c_wsd,c_wss???
    """
    
    sitepath=".";
    for x in sys.path:
        ix=x.find('site-packages')
        if( ix>=0 and x[ix:]=='site-packages'):
          sitepath=x;
          break;
    sitepath=sitepath+"\\WindPy.pth"
    # print('@@@@@@@@@@@@@@@  ',sitepath,' @@@@@@@@@@@@@@@')
    pathfile=open(sitepath)
    dllpath=pathfile.readlines();
    pathfile.close();

    sitepath=dllpath[0]+"\\WindPy.dll"    
    c_windlib=cdll.LoadLibrary(sitepath)

    #start
    c_start=c_windlib.start;
    c_start.restype=c_int32;
    c_start.argtypes=[c_wchar_p,c_wchar_p,c_int32]

    #stop
    c_stop=c_windlib.stop;
    c_stop.restype=c_int32;
    c_stop.argtypes=[]

    #stop
    c_isConnectionOK=c_windlib.isConnectionOK;
    c_isConnectionOK.restype=c_int32;
    c_isConnectionOK.argtypes=[]
    #c_isConnectionOK=staticmethod(c_isConnectionOK)

    #menu
    c_menu=c_windlib.menu;
    #c_menu.restype=c_int32;
    c_menu.argtypes=[c_wchar_p]

    c_wsd=c_windlib.wsd
    c_wsd.restype=POINTER(c_apiout);
    c_wsd.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p] #code,field,begintime,endtime,option

    c_wsq=c_windlib.wsq
    c_wsq.restype=POINTER(c_apiout);
    c_wsq.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p]#codes,fields,options

    c_wsq_asyn=c_windlib.wsq_asyn
    c_wsq_asyn.restype=POINTER(c_apiout);
    c_wsq_asyn.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p]#codes,fields,options

    c_tdq=c_windlib.tdq
    c_tdq.restype=POINTER(c_apiout);
    c_tdq.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p]#codes,fields,options

    c_tdq_asyn=c_windlib.tdq_asyn
    c_tdq_asyn.restype=POINTER(c_apiout);
    c_tdq_asyn.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p]#codes,fields,options

    c_bbq=c_windlib.bbq
    c_bbq.restype=POINTER(c_apiout);
    c_bbq.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p]#codes,fields,options

    c_bbq_asyn=c_windlib.bbq_asyn
    c_bbq_asyn.restype=POINTER(c_apiout);
    c_bbq_asyn.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p]#codes,fields,options

    c_wss=c_windlib.wss
    c_wss.restype=POINTER(c_apiout);
    c_wss.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p] #codes,fields,options


    c_wst=c_windlib.wst
    c_wst.restype=POINTER(c_apiout);
    c_wst.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p]#code,field,begintime,endtime,option

    c_wsi=c_windlib.wsi
    c_wsi.restype=POINTER(c_apiout);
    c_wsi.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p]#code,field,begintime,endtime,option

    c_tdays=c_windlib.tdays
    c_tdays.restype=POINTER(c_apiout);
    c_tdays.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p] #begintime,endtime,options

    c_tdayscount=c_windlib.tdayscount
    c_tdayscount.restype=POINTER(c_apiout);
    c_tdayscount.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p] #begintime,endtime,options

    c_tdaysoffset=c_windlib.tdaysoffset
    c_tdaysoffset.restype=POINTER(c_apiout);
    c_tdaysoffset.argtypes=[c_wchar_p,c_int32,c_wchar_p] #begintime,offset,options

    c_wset=c_windlib.wset
    c_wset.restype=POINTER(c_apiout);
    c_wset.argtypes=[c_wchar_p,c_wchar_p] #tablename,options
    
    c_weqs=c_windlib.weqs
    c_weqs.restype=POINTER(c_apiout);
    c_weqs.argtypes=[c_wchar_p,c_wchar_p] #filtername,options
    
    c_wpf=c_windlib.wpf
    c_wpf.restype=POINTER(c_apiout);
    c_wpf.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p] #productname,tablename,options           

    c_wupf=c_windlib.wupf
    c_wupf.restype=POINTER(c_apiout);
    c_wupf.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p] #PortfolioName,TradeDate,WindCode,Quantity,CostPrice,options           

    c_wpd=c_windlib.wpd
    c_wpd.restype=POINTER(c_apiout);
    c_wpd.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p] #PortfolioName,field,begintime,endtime,option

    c_wps=c_windlib.wps
    c_wps.restype=POINTER(c_apiout);
    c_wps.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p] #PortfolioName,fields,options

    c_htocode=c_windlib.htocode
    c_htocode.restype=POINTER(c_apiout);
    c_htocode.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p] #codes,sec_type,options

    c_tlogon=c_windlib.tLogon
    c_tlogon.restype=POINTER(c_apiout);
    c_tlogon.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p] #BrokerID,DepartmentID,LogonAccount,Password,AccountType,loptions           

    c_tlogout=c_windlib.tLogout
    c_tlogout.restype=POINTER(c_apiout);
    c_tlogout.argtypes=[c_wchar_p] #loptions           

    c_torder=c_windlib.tOrder
    c_torder.restype=POINTER(c_apiout);
    c_torder.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p] #SecurityCode,TradeSide,OrderPrice,OrderVolume,loptions           

    c_toperate=c_windlib.tOperate
    c_toperate.restype=POINTER(c_apiout);
    c_toperate.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p] #SecurityCode,OperateType,OrderVolume,loptions

    c_tcancel=c_windlib.tCancel
    c_tcancel.restype=POINTER(c_apiout);
    c_tcancel.argtypes=[c_wchar_p,c_wchar_p] #OrderNumber,loptions           

    c_tquery=c_windlib.tQuery
    c_tquery.restype=POINTER(c_apiout);
    c_tquery.argtypes=[c_wchar_p,c_wchar_p] #qrycode,loptions           

    c_getversion=c_windlib.getVersion
    c_getversion.restype=POINTER(c_apiout);
    c_getversion.argtypes=[] #           

    c_tmonitor=c_windlib.tMonitor
    c_tmonitor.restype=POINTER(c_apiout);
    c_tmonitor.argtypes=[c_wchar_p] #loptions
    
    c_free_data=c_windlib.free_data
    c_free_data.restype=None;
    c_free_data.argtypes=[POINTER(c_apiout)]

    c_setStateCallback=c_windlib.setStateCallback
    c_setStateCallback.restype=None;
    c_setStateCallback.argtypes=[c_StateChangedCallbackType] #callback

    c_readanydata=c_windlib.readanydata
    c_readanydata.restype=POINTER(c_apiout);
    c_readanydata.argtypes=None  
    
    c_readdata=c_windlib.readdata
    c_readdata.restype=POINTER(c_apiout);
    c_readdata.argtypes=[c_int64,c_int32] 

    c_cancelRequest=c_windlib.cancelRequest
    c_cancelRequest.restype=None;
    c_cancelRequest.argtypes=[c_int64]

    c_cleardata=c_windlib.cleardata
    c_cleardata.restype=None;
    c_cleardata.argtypes=[c_int64]

    c_bktstart=c_windlib.bktstart
    c_bktstart.restype=POINTER(c_apiout);
    c_bktstart.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p] #StrategyName,StartDate,EndDate,options

    c_bktquery=c_windlib.bktquery
    c_bktquery.restype=POINTER(c_apiout);
    c_bktquery.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p] #qrycode,qrytime,options

    c_bktorder=c_windlib.bktorder
    c_bktorder.restype=POINTER(c_apiout);
    c_bktorder.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p] #TradeTime,SecurityCode,TradeSide,TradeVol,options
    
    c_bktstatus=c_windlib.bktstatus
    c_bktstatus.restype=POINTER(c_apiout);
    c_bktstatus.argtypes=[c_wchar_p] #options
    
    c_bktend=c_windlib.bktend
    c_bktend.restype=POINTER(c_apiout);
    c_bktend.argtypes=[c_wchar_p] #options

    c_bktsummary=c_windlib.bktsummary
    c_bktsummary.restype=POINTER(c_apiout);
    c_bktsummary.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p] #BktID,View,options

    c_bktdelete=c_windlib.bktdelete
    c_bktdelete.restype=POINTER(c_apiout);
    c_bktdelete.argtypes=[c_wchar_p,c_wchar_p] #BktID,options

    c_bktstrategy=c_windlib.bktstrategy
    c_bktstrategy.restype=POINTER(c_apiout);
    c_bktstrategy.argtypes=[c_wchar_p] #options

    c_bktfocus=c_windlib.bktfocus
    c_bktfocus.restype=POINTER(c_apiout);
    c_bktfocus.argtypes=[c_wchar_p,c_wchar_p] #StrategyID,options
    
    c_bktshare=c_windlib.bktshare
    c_bktshare.restype=POINTER(c_apiout);
    c_bktshare.argtypes=[c_wchar_p,c_wchar_p] #StrategyID,options

    c_edb=c_windlib.edb
    c_edb.restype=POINTER(c_apiout);
    c_edb.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p] #code,begintime,endtime,option
    
    c_wappAuth=c_windlib.wappAuth
    c_wappAuth.restype=POINTER(c_apiout);
    c_wappAuth.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p] #appKey,appSecret,options
    
    c_wappMessage=c_windlib.wappMessage
    c_wappMessage.restype=POINTER(c_apiout);
    c_wappMessage.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p] #type_id,message,options
    
    c_wses=c_windlib.wses
    c_wses.restype=POINTER(c_apiout);
    c_wses.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p] #code,field,begintime,endtime,option
	
    c_wsee=c_windlib.wsee
    c_wsee.restype=POINTER(c_apiout);
    c_wsee.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p] #codes,fields,options
	
    c_wsed=c_windlib.wsed
    c_wsed.restype=POINTER(c_apiout);
    c_wsed.argtypes=[c_wchar_p,c_wchar_p,c_wchar_p] #codes,fields,options
	
    def asDateTime(v, asDate=False):
        #DLL?????????????+??????????
        #?????1899-12-30 00:00:00
        #???????double????, ???????, ????????????????????????????????????????????
        #???????500????, ????????????, ????????????, ??????????, dtAjust??????????????????500????
        dtAjust = datetime(1899, 12, 30, 0, 0, 0, 0) + timedelta(v, 0, 500)
        if asDate == True:
            #?????????????, ????? date ????????, ?????? time ????????
            return date(dtAjust.year, dtAjust.month, dtAjust.day)
        else:
            #????????????, ??? 1ms (?? 1000 ??s) ????????, ??????????
            return datetime(dtAjust.year, dtAjust.month, dtAjust.day, dtAjust.hour, dtAjust.minute, dtAjust.second, int(dtAjust.microsecond / 1000) * 1000)

    asDateTime=staticmethod(asDateTime)

    cleardata=c_cleardata;
    cancelRequest=c_cancelRequest;

    
    class WindData:
        """
        ???????????????????????????api????????C?????????????python??????????????????????????numpy??????
             ???????.ErrorCode ????????????0???????
                  ???????????????  .Codes ?????????? .Fields??????????.Times??????????.Data???????????
                  ??????????????  .Fields??????????.Data???????????
                    
        """
        def __init__(self):
            self.ErrorCode = 0
            self.StateCode = 0
            self.RequestID = 0
            self.Codes = list()  #list( string)
            self.Fields = list() #list( string)
            self.Times = list() #list( time)
            self.Data = list()  #list( list1,list2,list3,list4)
            self.asDate=False
            self.datatype=0; #0-->DataAPI output, 1-->tradeAPI output
            pass

        def __del__(self):
            pass    

        def __str__(self):
            def str1D(v1d):
                if( not(isinstance(v1d,list)) ):
                      return str(v1d);
                  
                outLen = len(v1d);
                if(outLen==0):
                    return '[]';
                outdot = 0;
                outx='';
                outr='[';
                if outLen>10 :
                    outLen = 10;
                    outdot = 1;

                
                for x in v1d[0:outLen]:
                  try:    
                    outr = outr + outx + str(x);
                    outx=',';
                  except UnicodeEncodeError:
                    outr = outr + outx + repr(x);
                    outx=',';

                if outdot>0 :
                    outr = outr + outx + '...';
                outr = outr + ']';
                return outr;

            def str2D(v2d):
                #v2d = str(v2d_in);
                outLen = len(v2d);
                if(outLen==0):
                    return '[]';
                outdot = 0;
                outx='';
                outr='[';
                if outLen>10 :
                    outLen = 10;
                    outdot = 1;
                    
                for x in v2d[0:outLen]:
                   outr = outr + outx + str1D(x);
                   outx=',';

                if outdot>0 :
                    outr = outr + outx + '...';
                outr = outr + ']';
                return outr;

            a=".ErrorCode=%d"%self.ErrorCode
            if(self.datatype==0):
                if(self.StateCode!=0): a=a+ "\n.StateCode=%d"%self.StateCode
                if(self.RequestID!=0): a=a+ "\n.RequestID=%d"%self.RequestID
                if(len(self.Codes)!=0):a=a+"\n.Codes="+str1D(self.Codes)
                if(len(self.Fields)!=0): a=a+"\n.Fields="+str1D(self.Fields)
                if(len(self.Times)!=0):                 
                    if(self.asDate):a=a+ "\n.Times="+str1D([ format(x,'%Y%m%d') for x in self.Times])
                    else:
                        a=a+ "\n.Times="+str1D([ format(x,'%Y%m%d %H:%M:%S') for x in self.Times])
            else:
                a=a+"\n.Fields="+str1D(self.Fields)
                
            a=a+"\n.Data="+str2D(self.Data)
            return a;    


        def __format__(self,fmt):
            return str(self);
        def __repr__(self):
            return str(self);
        
        def clear(self):
            self.ErrorCode = 0
            self.StateCode = 0
            self.RequestID = 0
            self.Codes = list()  #list( string)
            self.Fields = list() #list( string)
            self.Times = list() #list( time)
            self.Data = list()  #list( list1,list2,list3,list4)
            
        def setErrMsg(self,errid,msg):
            self.clear();
            self.ErrorCode = errid;
            self.Data=[msg];
        def __getTotalCount(self,f):
            if((f.vt & VT_ARRAY ==0) or (f.parray == 0) or (f.parray[0].cDims==0)):
                return 0;

            totalCount=1;
            for i in range(f.parray[0].cDims) :
                totalCount = totalCount * f.parray[0].rgsabound[i].cElements;
            return totalCount;

        def __getColsCount(self,f,index=0):
            if((f.vt & VT_ARRAY ==0) or (f.parray == 0) or (index<f.parray[0].cDims)):
                return 0;

            return f.parray[0].rgsabound[index].cElements;
            
        def __getVarientValue(self,data):
            ltype = data.vt ;
            if ltype in [VT_I2,VT_UI2]:
                return data.iVal;
            if( ltype in [VT_I4,VT_UI4,VT_INT,VT_UINT]):
                return data.lVal;
            if( ltype in [VT_I8,VT_UI8]):
                return data.llVal;
            if( ltype in [VT_UI1,VT_I1]):
                return data.bVal;

            if( ltype in [VT_R4]):
                return data.fltVal;
            
            if( ltype in [VT_R8]):
                return data.dblVal;
            
            if( ltype in [VT_DATE]):
                return w.asDateTime(data.date);
                    
            if( ltype in [VT_BSTR]):
                 return data.bstrVal;

            return None;

            
        def __tolist(self,data,basei=0,diff=1):
            """:
            ??????dll????codes,fields,times ???list????
            data ?c_variant
            """
            totalCount = self.__getTotalCount(data);
            if(totalCount ==0): # or data.parray[0].cDims<1):
                return list();

            ltype = data.vt & VT_TYPEMASK;
            if ltype in [VT_I2,VT_UI2] :
                return data.parray[0].piVal[basei:totalCount:diff];
            if( ltype in [VT_I4,VT_UI4,VT_INT,VT_UINT]):
                return data.parray[0].plVal[basei:totalCount:diff];
            if( ltype in [VT_I8,VT_UI8]):
                return data.parray[0].pllVal[basei:totalCount:diff];        
            if( ltype in [VT_UI1,VT_I1]):
                return data.parray[0].pbVal[basei:totalCount:diff];        

            if( ltype in [VT_R4]):
                return data.parray[0].pfltVal[basei:totalCount:diff];        
            
            if( ltype in [VT_R8]):
                return data.parray[0].pdblVal[basei:totalCount:diff];        
            
            if( ltype in [VT_DATE]):
                return [w.asDateTime(x, self.asDate) for x in data.parray[0].pdate[basei:totalCount:diff]];
                    
            if( ltype in [VT_BSTR]):
                return data.parray[0].pbstrVal[basei:totalCount:diff];

            if(ltype in [VT_VARIANT]):
                return [self.__getVarientValue(x) for x in data.parray[0].pvarVal[basei:totalCount:diff]];

            return list();
            
          

        #bywhich=0 default,1 code, 2 field, 3 time
        #indata: POINTER(c_apiout)
        def set(self,indata,bywhich=0,asdate=None,datatype=None):
            self.clear();
            if( indata == 0):
                self.ErrorCode = 1;
                return;
            
            if(asdate==True): self.asDate = True
            if(datatype==None): datatype=0;
            if(datatype<=2): self.datatype=datatype;

            self.ErrorCode = indata[0].ErrorCode
            self.Fields = self.__tolist(indata[0].Fields);
            self.StateCode = indata[0].StateCode
            self.RequestID = indata[0].RequestID
            self.Codes = self.__tolist(indata[0].Codes);
            self.Times = self.__tolist(indata[0].Times);
##            if(self.datatype==0):# for data api output
            if (1==1):
                codeL=len(self.Codes)
                fieldL=len(self.Fields)
                timeL=len(self.Times)
                datalen=self.__getTotalCount(indata[0].Data);
                minlen=min(codeL,fieldL,timeL);

                if( datatype == 2 ):
                    self.Data=self.__tolist(indata[0].Data);
                    return;

                if( datalen != codeL*fieldL*timeL or minlen==0 ):
                    return ;

                if(minlen!=1):
                    self.Data=self.__tolist(indata[0].Data);
                    return;

                if(bywhich>3):
                    bywhich=0;

                if(codeL==1 and not( bywhich==2 and fieldL==1)  and not( bywhich==3 and timeL==1) ):
                    #row=time; col=field;
                    self.Data=[self.__tolist(indata[0].Data,i,fieldL) for i in range(fieldL)];
                    return
                if(timeL ==1 and not ( bywhich==2 and fieldL==1) ):
                    self.Data=[self.__tolist(indata[0].Data,i,fieldL) for i in range(fieldL)];
                    return

                if(fieldL==1 ):
                    self.Data=[self.__tolist(indata[0].Data,i,codeL) for i in range(codeL)];
                    return
                
                self.Data=self.__tolist(indata[0].Data);
##            else:#for trade api output
##                fieldL=len(self.Fields)
##                datalen=self.__getTotalCount(indata[0].Data);
##                colsLen=self.__getColsCount(indata[0].Data);
##
##                if( datalen != colsLen or datalen==0):
##                    return ;
##
##                #if(fieldL!=1):
##                #    self.Data=self.__tolist(indata[0].Data);
##                #    return;
##
##                self.Data=[self.__tolist(indata[0].Data,i,fieldL) for i in range(fieldL)];
##                return
               
            return;

            
    def __targ2str(arg):
        if(arg==None): return [""];
        if(arg==""): return [""];
        if(isinstance(arg,str)): return [arg];
        if(isinstance(arg,list)): return [str(x) for x in arg];
        if(isinstance(arg,tuple)): return [str(x) for x in arg];
        if(isinstance(arg,float) or isinstance(arg,int)): return [str(arg)];
        if( str(type(arg)) == "<type 'unicode'>" ): return [arg];
        return None;
    __targ2str=staticmethod(__targ2str)
    
    def __targArr2str(arg):    
        v = w.__targ2str(arg);
        if(v==None):return None;
        return "$$".join(v);
    __targArr2str=staticmethod(__targArr2str)

    def __dargArr2str(arg):    
        v = w.__targ2str(arg);
        if(v==None):return None;
        return ";".join(v);
    __dargArr2str=staticmethod(__dargArr2str)

    def __d2options(options,arga,argb):
        options = w.__dargArr2str(options);
        if(options==None): return None;

        for i in range(len(arga)):
            v= w.__dargArr2str(arga[i]);
            if(v==None):
                continue;
            else:
                if(options==""):
                    options = v;
                else:
                    options = options+";"+v;
         
        keys=argb.keys();
        for key in keys:
            v =w.__dargArr2str(argb[key]);
            if(v==None or v==""):
                continue;
            else:
                if(options==""):
                    options = str(key)+"="+v;
                else:
                    options = options+";"+str(key)+"="+v;
        return options;
    __d2options=staticmethod(__d2options)

    def __t2options(options,arga,argb):
        options = w.__dargArr2str(options);
        if(options==None): return None;

        for i in range(len(arga)):
            v= w.__dargArr2str(arga[i]);
            if(v==None):
                continue;
            else:
                if(options==""):
                    options = v;
                else:
                    options = options+";"+v;
         
        keys=argb.keys();
        for key in keys:
            v =w.__targArr2str(argb[key]);
            if(v==None or v==""):
                continue;
            else:
                if(options==""):
                    options = str(key)+"="+v;
                else:
                    options = options+";"+str(key)+"="+v;
        return options;
    __t2options=staticmethod(__t2options)
    
    def isconnected():
        """???????????w.start??"""
        r = w.c_isConnectionOK()
        if r !=0: return True;
        else: return False;
    isconnected=staticmethod(isconnected)
        
    def menu(menu=""):
        #c_menu(menu)
        return
    menu=staticmethod(menu)    
        
    def start(waitTime=120, showmenu=True):
            """??WindPy??waitTime??????????"""
            outdata=w.WindData();
            if(w.isconnected()):
                outdata.setErrMsg(0,"Already conntected!");
                return outdata;

            #w.global.Functions<<-list()
            
            err=w.c_start("","",waitTime*1000);
            lmsg="";
            if(err==0):
                lmsg="OK!"
            elif(err==-40520009):
                lmsg="WBox lost!";
            elif(err==-40520008):
                lmsg="Timeout Error!";
            elif(err==-40520005):
                lmsg="No Python API Authority!";
            elif(err==-40520004):
                lmsg="Login Failed!";
            elif(err==-40520014):
                lmsg="Please Logon iWind firstly!";
            else:
                lmsg="Start Error!";
            
            if(err==0):
                print("Welcome to use Wind Quant API for Python (WindPy)!");
                print("");
                print("COPYRIGHT (C) 2017 WIND INFORMATION CO., LTD. ALL RIGHTS RESERVED.");
                print("IN NO CIRCUMSTANCE SHALL WIND BE RESPONSIBLE FOR ANY DAMAGES OR LOSSES CAUSED BY USING WIND QUANT API FOR Python.")
                
                if(showmenu):
                    w.menu();

            outdata.setErrMsg(err,lmsg);
            return outdata;        
    start=staticmethod(start)

    def close():
        """??WindPy??"""
        w.c_stop()
    close=staticmethod(close)

    def stop():
        """??WindPy??"""
        w.c_stop()
    stop=staticmethod(stop)



    def wsd(codes, fields, beginTime=None, endTime=None, options=None,*arga,**argb):
            """wsd???????????"""
            if(endTime==None):  endTime = datetime.today().strftime("%Y-%m-%d")
            if(beginTime==None):  beginTime = endTime            
            codes = w.__dargArr2str(codes);
            fields = w.__dargArr2str(fields);
            options = w.__t2options(options,arga,argb);
            if(codes==None or fields==None or options==None):
                print('Invalid arguments!');
                return;
            
            if(isinstance(beginTime,date) or isinstance(beginTime,datetime)):
                beginTime=beginTime.strftime("%Y-%m-%d")

            if(isinstance(endTime,date) or isinstance(endTime,datetime)):
                endTime=endTime.strftime("%Y-%m-%d")

            out =w.WindData();
            apiout=w.c_wsd(codes,fields,beginTime,endTime,options);
            out.set(apiout,1,asdate=True);
            w.c_free_data(apiout);
            
            return out;
    wsd=staticmethod(wsd)
        
    def wst(codes, fields, beginTime=None, endTime=None, options=None,*arga,**argb):
            """wst???????????"""
            if(endTime==None): endTime = datetime.today().strftime("%Y%m%d %H:%M:%S")
            if(beginTime==None):  beginTime = endTime   
            codes = w.__dargArr2str(codes);
            fields = w.__dargArr2str(fields);
            options = w.__t2options(options,arga,argb);
            if(codes==None or fields==None or options==None):
                print('Invalid arguments!');
                return;
            
            if(isinstance(beginTime,date) or isinstance(beginTime,datetime)):
                beginTime=beginTime.strftime("%Y%m%d %H:%M:%S")

            if(isinstance(endTime,date) or isinstance(endTime,datetime)):
                endTime=endTime.strftime("%Y%m%d %H:%M:%S")

            out =w.WindData();
            apiout=w.c_wst(codes,fields,beginTime,endTime,options);
            out.set(apiout,1);
            w.c_free_data(apiout);
            
            return out;
    wst=staticmethod(wst)
        
    def wsi(codes, fields, beginTime=None, endTime=None, options=None,*arga,**argb):
            """wsi???????????"""
            if(endTime==None): endTime = datetime.today().strftime("%Y%m%d %H:%M:%S")
            if(beginTime==None):  beginTime = endTime   
            codes = w.__dargArr2str(codes);
            fields = w.__dargArr2str(fields);
            options = w.__t2options(options,arga,argb);
            if(codes==None or fields==None or options==None):
                print('Invalid arguments!');
                return;
            
            if(isinstance(beginTime,date) or isinstance(beginTime,datetime)):
                beginTime=beginTime.strftime("%Y%m%d %H:%M:%S")

            if(isinstance(endTime,date) or isinstance(endTime,datetime)):
                endTime=endTime.strftime("%Y%m%d %H:%M:%S")

            out =w.WindData();
            apiout=w.c_wsi(codes,fields,beginTime,endTime,options);
            out.set(apiout,1);
            w.c_free_data(apiout);
            
            return out;
    wsi=staticmethod(wsi)

    def tdays(beginTime=None, endTime=None, options=None,*arga,**argb):
            """tdays????????????"""
            if(endTime==None): endTime = datetime.today().strftime("%Y%m%d")
            if(beginTime==None):  beginTime = endTime   
            options = w.__t2options(options,arga,argb);
            if(endTime==None or beginTime==None or options==None):
                print('Invalid arguments!');
                return;
            
            if(isinstance(beginTime,date) or isinstance(beginTime,datetime)):
                beginTime=beginTime.strftime("%Y%m%d")
            if(isinstance(endTime,date) or isinstance(endTime,datetime)):
                endTime=endTime.strftime("%Y%m%d")

            out =w.WindData();
            apiout=w.c_tdays(beginTime,endTime,options);
            out.set(apiout,1,asdate=True);
            w.c_free_data(apiout);
            
            return out;
    tdays=staticmethod(tdays)

    def tdayscount(beginTime=None, endTime=None, options=None,*arga,**argb):
            """tdayscount?????????"""
            if(endTime==None): endTime = datetime.today().strftime("%Y%m%d")
            if(beginTime==None):  beginTime = endTime 
            options = w.__t2options(options,arga,argb);
            if(endTime==None or beginTime==None or options==None):
                print('Invalid arguments!');
                return;
            
            if(isinstance(beginTime,date) or isinstance(beginTime,datetime)):
                beginTime=beginTime.strftime("%Y%m%d")
            if(isinstance(endTime,date) or isinstance(endTime,datetime)):
                endTime=endTime.strftime("%Y%m%d")

            out =w.WindData();
            apiout=w.c_tdayscount(beginTime,endTime,options);
            out.set(apiout,1,asdate=True);
            w.c_free_data(apiout);
            
            return out;
    tdayscount=staticmethod(tdayscount)

    def tdaysoffset(offset, beginTime=None, options=None,*arga,**argb):
            """tdayscount??????????"""
            if(beginTime==None): beginTime = datetime.today().strftime("%Y%m%d")

            options = w.__t2options(options,arga,argb);
            if(beginTime==None or options==None):
                print('Invalid arguments!');
                return;
            
            if(isinstance(beginTime,date) or isinstance(beginTime,datetime)):
                beginTime=beginTime.strftime("%Y%m%d")

            out =w.WindData();
            apiout=w.c_tdaysoffset(beginTime,offset,options);
            out.set(apiout,1,asdate=True);
            w.c_free_data(apiout);
            
            return out;
    tdaysoffset=staticmethod(tdaysoffset)

    def wset(tablename, options=None,*arga,**argb):
            """wset????????"""
            tablename = w.__dargArr2str(tablename);
            options = w.__t2options(options,arga,argb);
            if(tablename==None or options==None):
                print('Invalid arguments!');
                return;
            
            out =w.WindData();
            apiout=w.c_wset(tablename,options);
            out.set(apiout,3,asdate=True);
            w.c_free_data(apiout);
            
            return out;
    wset=staticmethod(wset)

    def weqs(filtername, options=None,*arga,**argb):
            """weqs?????????????"""
            filtername = w.__dargArr2str(filtername);
            options = w.__t2options(options,arga,argb);
            if(filtername==None or options==None):
                print('Invalid arguments!');
                return;
            
            out =w.WindData();
            apiout=w.c_weqs(filtername,options);
            out.set(apiout,3,asdate=True);
            w.c_free_data(apiout);
            
            return out;
    weqs=staticmethod(weqs)    
    
    def wpf(productname,tablename, options=None,*arga,**argb):
            """wpf??????"""
            productname = w.__dargArr2str(productname);
            tablename = w.__dargArr2str(tablename);
            options = w.__t2options(options,arga,argb);
            if(productname==None or tablename==None or options==None):
                print('Invalid arguments!');
                return;            
            
            out =w.WindData();
            apiout=w.c_wpf(productname,tablename,options);
            out.set(apiout,3);
            w.c_free_data(apiout);
            
            return out;
    wpf=staticmethod(wpf)   

    def wupf(PortfolioName,TradeDate,WindCode,Quantity,CostPrice, options=None,*arga,**argb):
            """wpf??????"""
            PortfolioName = w.__dargArr2str(PortfolioName);
            TradeDate = w.__dargArr2str(TradeDate);
            WindCode = w.__dargArr2str(WindCode);
            Quantity = w.__dargArr2str(Quantity);
            CostPrice = w.__dargArr2str(CostPrice);
            options = w.__t2options(options,arga,argb);
            if(PortfolioName==None or TradeDate==None or WindCode==None or Quantity==None or CostPrice==None or options==None):
                print('Invalid arguments!');
                return;            
            
            out =w.WindData();
            apiout=w.c_wupf(PortfolioName,TradeDate,WindCode,Quantity,CostPrice,options);
            out.set(apiout,3,datatype=1);
            w.c_free_data(apiout);
            
            return out;
    wupf=staticmethod(wupf)   

    def wpd(PortfolioName, fields, beginTime=None, endTime=None, options=None,*arga,**argb):
            """wpd??????"""
            if(endTime==None):  endTime = datetime.today().strftime("%Y-%m-%d")
            if(beginTime==None):  beginTime = endTime            
            PortfolioName = w.__dargArr2str(PortfolioName);
            fields = w.__dargArr2str(fields);
            options = w.__t2options(options,arga,argb);
            if(PortfolioName==None or fields==None or options==None):
                print('Invalid arguments!');
                return;
            
            if(isinstance(beginTime,date) or isinstance(beginTime,datetime)):
                beginTime=beginTime.strftime("%Y-%m-%d")

            if(isinstance(endTime,date) or isinstance(endTime,datetime)):
                endTime=endTime.strftime("%Y-%m-%d")

            out =w.WindData();
            apiout=w.c_wpd(PortfolioName,fields,beginTime,endTime,options);
            out.set(apiout,1,asdate=True);
            w.c_free_data(apiout);
            
            return out;
    wpd=staticmethod(wpd)

    def wps(PortfolioName, fields, options=None,*arga,**argb):
            """wps??????"""
            PortfolioName = w.__dargArr2str(PortfolioName);
            fields = w.__dargArr2str(fields);
            options = w.__t2options(options,arga,argb);
            if(PortfolioName==None or fields==None or options==None):
                print('Invalid arguments!');
                return;

            out =w.WindData();
            apiout=w.c_wps(PortfolioName,fields,options);
            out.set(apiout,3);
            w.c_free_data(apiout);
            
            return out;
    wps=staticmethod(wps)

    def wsq(codes, fields, options=None, func=None,*arga,**argb):
            """wsq?????????"""
            codes = w.__dargArr2str(codes);
            fields = w.__dargArr2str(fields);
            options = w.__t2options(options,arga,argb);
            if(codes==None or fields==None or options==None):
                print('Invalid arguments!');
                return;
            
            if(not callable(func)):
                out =w.WindData();
                apiout=w.c_wsq(codes,fields,options);
                out.set(apiout,3);
                w.c_free_data(apiout);
            else:
                out =w.WindData();
                apiout=w.c_wsq_asyn(codes,fields,options);
                out.set(apiout,3);
                w.c_free_data(apiout);                
                if(out.ErrorCode ==0):
                    global gFunctionDict
                    gFuncDictMutex.acquire();
                    gFunctionDict[out.RequestID] = func;
                    gFuncDictMutex.release();
            
            return out;
    wsq=staticmethod(wsq)

    def tdq(codes, fields, options=None, func=None,*arga,**argb):
            """tdq?????????"""
            codes = w.__dargArr2str(codes);
            fields = w.__dargArr2str(fields);
            options = w.__t2options(options,arga,argb);
            if(codes==None or fields==None or options==None):
                print('Invalid arguments!');
                return;
            
            if(not callable(func)):
                out =w.WindData();
                apiout=w.c_tdq(codes,fields,options);
                out.set(apiout,3);
                w.c_free_data(apiout);
            else:
                out =w.WindData();
                apiout=w.c_tdq_asyn(codes,fields,options);
                out.set(apiout,3);
                w.c_free_data(apiout);                
                if(out.ErrorCode ==0):
                    global gFunctionDict
                    gFuncDictMutex.acquire();
                    gFunctionDict[out.RequestID] = func;
                    gFuncDictMutex.release();
            
            return out;
    tdq=staticmethod(tdq)

    def bbq(codes, fields, options=None, func=None,*arga,**argb):
            """bbq???????????"""
            codes = w.__dargArr2str(codes);
            fields = w.__dargArr2str(fields);
            options = w.__t2options(options,arga,argb);
            if(codes==None or fields==None or options==None):
                print('Invalid arguments!');
                return;
            
            if(not callable(func)):
                out =w.WindData();
                apiout=w.c_bbq(codes,fields,options);
                out.set(apiout,3);
                w.c_free_data(apiout);
            else:
                out =w.WindData();
                apiout=w.c_bbq_asyn(codes,fields,options);
                out.set(apiout,3);
                w.c_free_data(apiout);                
                if(out.ErrorCode ==0):
                    global gFunctionDict
                    gFuncDictMutex.acquire();
                    gFunctionDict[out.RequestID] = func;
                    gFuncDictMutex.release();
            
            return out;
    bbq=staticmethod(bbq)

    def wss(codes, fields, options=None,*arga,**argb):
            """wss???????????"""
            codes = w.__dargArr2str(codes);
            fields = w.__dargArr2str(fields);
            options = w.__t2options(options,arga,argb);
            if(codes==None or fields==None or options==None):
                print('Invalid arguments!');
                return;

            out =w.WindData();
            apiout=w.c_wss(codes,fields,options);
            out.set(apiout,3);
            w.c_free_data(apiout);
            
            return out;
    wss=staticmethod(wss)
    
    def htocode(codes, sec_type, options=None,*arga,**argb):
            codes = w.__dargArr2str(codes);
            sec_type = w.__dargArr2str(sec_type);
            options = w.__t2options(options,arga,argb);
            if(codes==None or sec_type==None or options==None):
                print('Invalid arguments!');
                return;
            
            out =w.WindData();
            apiout=w.c_htocode(codes,sec_type,options);
            out.set(apiout,3,asdate=True);
            w.c_free_data(apiout);
            
            return out;
    htocode=staticmethod(htocode)
    
    def readdata(reqid,isdata=1):
        """readdata???????id?reqid??????"""
        out =w.WindData();
        apiout=w.c_readdata(reqid,isdata);
        if( isdata==1 ):
          out.set(apiout,3);
        else:
          out.set(apiout,3,datatype=2);
        w.c_free_data(apiout);
        return out
    readdata=staticmethod(readdata)

    def readanydata():
        """readdata???????????????"""
        out =w.WindData();
        apiout=w.c_readanydata();
        out.set(apiout,3);
        w.c_free_data(apiout);
        return out
    readanydata=staticmethod(readanydata)    


        

    def tlogon(BrokerID, DepartmentID, LogonAccount, Password, AccountType,options=None,func=None,*arga,**argb):
            BrokerID = w.__targArr2str(BrokerID);
            DepartmentID = w.__targArr2str(DepartmentID);
            LogonAccount = w.__targArr2str(LogonAccount);
            Password = w.__targArr2str(Password);
            AccountType = w.__targArr2str(AccountType);
            
            options = w.__t2options(options,arga,argb);

            if(callable(func)):
              options += ';PushCallBack=A';
              gTradeFuncMutex.acquire();
              gTradeFunctionDict[0] = func;
              gTradeFuncMutex.release();
            
            if(BrokerID==None or DepartmentID==None or LogonAccount==None or Password==None or AccountType==None or options==None):
                print('Invalid arguments!');
                return;
            
            out =w.WindData();
            apiout=w.c_tlogon(BrokerID,DepartmentID,LogonAccount,Password,AccountType,options);
            out.set(apiout,3,datatype=1);
            w.c_free_data(apiout);
            
            if(callable(func)):
                gTradeFuncMutex.acquire();
                gTradeFunctionDict[0] = None;
                gTradeFuncMutex.release();
                Logonid = 0;
                for i in range(len(out.Fields)):
                    if(out.Fields[i]=='LogonID'):
                        Logonid = out.Data[i][0];
                if( Logonid != 0 ):
                    gTradeFuncMutex.acquire();
                    gTradeFunctionDict[Logonid] = func;
                    gTradeFuncMutex.release();
                    
            return out;
    tlogon=staticmethod(tlogon)      


    def tlogout(LogonID=None,options=None,*arga,**argb):
            LogonID = w.__targArr2str(LogonID);
            if(LogonID!=None and LogonID!=''):
                argb['LogonID']=LogonID;
                
            options = w.__t2options(options,arga,argb);
            if(LogonID==None or options==None):
                print('Invalid arguments!');
                return;
            
            out =w.WindData();
            apiout=w.c_tlogout(options);
            out.set(apiout,3,datatype=1);
            w.c_free_data(apiout);
            
            return out;
    tlogout=staticmethod(tlogout)
    
    def torder(SecurityCode, TradeSide, OrderPrice, OrderVolume,options=None,*arga,**argb):
            SecurityCode = w.__targArr2str(SecurityCode);
            TradeSide = w.__targArr2str(TradeSide);
            OrderPrice = w.__targArr2str(OrderPrice);
            OrderVolume = w.__targArr2str(OrderVolume);
            options = w.__t2options(options,arga,argb);
            if(SecurityCode==None or TradeSide==None or OrderPrice==None or OrderVolume==None or options==None):
                print('Invalid arguments!');
                return;
            
            out =w.WindData();
            apiout=w.c_torder(SecurityCode,TradeSide,OrderPrice,OrderVolume,options);
            out.set(apiout,3,datatype=1);
            w.c_free_data(apiout);
            
            return out;
    torder=staticmethod(torder)  
    
    def toperate(SecurityCode, OperateType, OrderVolume,options=None,*arga,**argb):
            SecurityCode = w.__targArr2str(SecurityCode);
            OperateType = w.__targArr2str(OperateType);
            OrderVolume = w.__targArr2str(OrderVolume);
            options = w.__t2options(options,arga,argb);
            if(OperateType==None or OrderVolume==None):
                print('Invalid arguments!');
                return;
            
            out =w.WindData();
            apiout=w.c_toperate(SecurityCode,OperateType,OrderVolume,options);
            out.set(apiout,3,datatype=1);
            w.c_free_data(apiout);
            
            return out;
    toperate=staticmethod(toperate) 
    
    def tcancel(OrderNumber, options=None,*arga,**argb):
            OrderNumber = w.__targArr2str(OrderNumber);
            options = w.__t2options(options,arga,argb);
            if(OrderNumber==None or options==None):
                print('Invalid arguments!');
                return;
            
            out =w.WindData();
            apiout=w.c_tcancel(OrderNumber,options);
            out.set(apiout,3,datatype=1);
            w.c_free_data(apiout);
            
            return out;
    tcancel=staticmethod(tcancel)

    def tquery(qrycode, options=None,*arga,**argb):
            if(qrycode!=None):
               qrycode = str(qrycode);
            options = w.__t2options(options,arga,argb);
            if(qrycode==None or options==None):
                print('Invalid arguments!');
                return;
            
            out =w.WindData();
            apiout=w.c_tquery(qrycode,options);
            out.set(apiout,3,datatype=1);
            w.c_free_data(apiout);
            
            return out;
    tquery=staticmethod(tquery)

    def tmonitor(options=None,*arga,**argb):
            options = w.__t2options(options,arga,argb);
            if(options==None):
                print('Invalid arguments!');
                return;
            
            out =w.WindData();
            apiout=w.c_tmonitor(options);
            out.set(apiout,3,datatype=1);
            w.c_free_data(apiout);
            
            return out;
    tmonitor=staticmethod(tmonitor)
    
    def getversion():
            apiout=w.c_getversion();
            out =w.WindData();
            out.set(apiout,3,datatype=1);
            w.c_free_data(apiout);

            try:
                return out.Data[0][0]+"WindPy.py version 1.0\n";
            except:
                return "Error in getversion.\nWindPy.py version 1.0\n";

    getversion=staticmethod(getversion)

    def bktstart(StrategyName, StartDate, EndDate, options=None,*arga,**argb):
            if(StrategyName!=None):
               StrategyName = str(StrategyName);
               
            if(isinstance(StartDate,date) or isinstance(StartDate,datetime)):
                StartDate=StartDate.strftime('%Y-%m-%d %H:%M:%S')

            if(isinstance(EndDate,date) or isinstance(EndDate,datetime)):
                EndDate=EndDate.strftime('%Y-%m-%d %H:%M:%S')

            StrategyName = w.__dargArr2str(StrategyName);
            StartDate = w.__dargArr2str(StartDate);
            EndDate = w.__dargArr2str(EndDate);            
            
            options = w.__d2options(options,arga,argb);
            if(StrategyName==None or StartDate==None or EndDate==None or options==None):
                print('Invalid arguments!');
                return;
            
            out =w.WindData();
            apiout=w.c_bktstart(StrategyName,StartDate, EndDate,options);
            out.set(apiout,3,datatype=2);
            w.c_free_data(apiout);
            
            return out;
    bktstart=staticmethod(bktstart)

    def bktquery(qrycode, qrytime, options=None,*arga,**argb):
            if(isinstance(qrytime,date) or isinstance(qrytime,datetime)):
                qrytime=qrytime.strftime('%Y-%m-%d %H:%M:%S')

            qrycode = w.__dargArr2str(qrycode);
            qrytime = w.__dargArr2str(qrytime);
            
            options = w.__d2options(options,arga,argb);
            if(qrycode==None or qrytime==None or options==None):
                print('Invalid arguments!');
                return;
            
            out =w.WindData();
            apiout=w.c_bktquery(qrycode, qrytime, options);
            out.set(apiout,3,datatype=2);
            w.c_free_data(apiout);
            
            return out;
    bktquery=staticmethod(bktquery)

    def bktorder(TradeTime, SecurityCode, TradeSide, TradeVol, options=None,*arga,**argb):
            if(isinstance(TradeTime,date) or isinstance(TradeTime,datetime)):
                TradeTime=TradeTime.strftime('%Y-%m-%d %H:%M:%S')

            SecurityCode = w.__dargArr2str(SecurityCode);
            TradeSide = w.__dargArr2str(TradeSide);
            TradeVol = w.__dargArr2str(TradeVol);
            TradeTime = w.__dargArr2str(TradeTime);
            
            options = w.__d2options(options,arga,argb);
            if(SecurityCode==None or TradeSide==None or TradeVol==None or TradeTime==None or options==None):
                print('Invalid arguments!');
                return;
            
            out =w.WindData();
            apiout=w.c_bktorder(TradeTime,SecurityCode, TradeSide,TradeVol, options);
            out.set(apiout,3,datatype=2);
            w.c_free_data(apiout);
            
            return out;
    bktorder=staticmethod(bktorder)    
        

    def bktstatus(options=None,*arga,**argb):
            options = w.__d2options(options,arga,argb);
            if(options==None):
                print('Invalid arguments!');
                return;
            
            out =w.WindData();
            apiout=w.c_bktstatus(options);
            out.set(apiout,3,datatype=2);
            w.c_free_data(apiout);
            
            return out;
    bktstatus=staticmethod(bktstatus)

    def bktend(options=None,*arga,**argb):
            options = w.__d2options(options,arga,argb);
            if(options==None):
                print('Invalid arguments!');
                return;
            
            out =w.WindData();
            apiout=w.c_bktend(options);
            out.set(apiout,3,datatype=2);
            w.c_free_data(apiout);
            
            return out;
    bktend=staticmethod(bktend)

    def bktsummary(BktID,View, options=None,*arga,**argb):
            BktID = w.__dargArr2str(BktID);
            View = w.__dargArr2str(View);

            options = w.__d2options(options,arga,argb);
            if(BktID==None or View==None or options==None):
                print('Invalid arguments!');
                return;
            
            out =w.WindData();
            apiout=w.c_bktsummary(BktID,View, options);
            out.set(apiout,3,datatype=2);
            w.c_free_data(apiout);
            
            return out;
    bktsummary=staticmethod(bktsummary)

    def bktdelete(BktID, options=None,*arga,**argb):
            BktID = w.__dargArr2str(BktID);

            options = w.__d2options(options,arga,argb);
            if(BktID==None or options==None):
                print('Invalid arguments!');
                return;
            
            out =w.WindData();
            apiout=w.c_bktdelete(BktID, options);
            out.set(apiout,3,datatype=2);
            w.c_free_data(apiout);
            
            return out;
    bktdelete=staticmethod(bktdelete)

    def bktstrategy(options=None,*arga,**argb):
            options = w.__d2options(options,arga,argb);
            
            out =w.WindData();
            apiout=w.c_bktstrategy(options);
            out.set(apiout,3,datatype=2);
            w.c_free_data(apiout);
            
            return out;
    bktstrategy=staticmethod(bktstrategy)

    def bktfocus(StrategyID, options=None,*arga,**argb):
            StrategyID = w.__dargArr2str(StrategyID);
            options = w.__d2options(options,arga,argb);
            if(StrategyID==None or options==None):
                print('Invalid arguments!');
                return;
            
            out =w.WindData();
            apiout=w.c_bktfocus(StrategyID, options);
            out.set(apiout,3,datatype=2);
            w.c_free_data(apiout);
            
            return out;
    bktfocus=staticmethod(bktfocus)    

    def bktshare(StrategyID, options=None,*arga,**argb):
            StrategyID = w.__dargArr2str(StrategyID);
            options = w.__d2options(options,arga,argb);
            if(StrategyID==None or options==None):
                print('Invalid arguments!');
                return;
            
            out =w.WindData();
            apiout=w.c_bktshare(StrategyID, options);
            out.set(apiout,3,datatype=2);
            w.c_free_data(apiout);
            
            return out;
    bktshare=staticmethod(bktshare)        
    
    
    def edb(codes, beginTime=None, endTime=None, options=None,*arga,**argb):
            """edb???"""
            if(endTime==None):  endTime = datetime.today().strftime("%Y-%m-%d")
            if(beginTime==None):  beginTime = endTime            
            codes = w.__dargArr2str(codes);
            options = w.__t2options(options,arga,argb);
            if(codes==None or options==None):
                print('Invalid arguments!');
                return;
            
            if(isinstance(beginTime,date) or isinstance(beginTime,datetime)):
                beginTime=beginTime.strftime("%Y-%m-%d")

            if(isinstance(endTime,date) or isinstance(endTime,datetime)):
                endTime=endTime.strftime("%Y-%m-%d")

            out =w.WindData();
            apiout=w.c_edb(codes,beginTime,endTime,options);
            out.set(apiout,1,asdate=True);
            w.c_free_data(apiout);
            
            return out;
    edb=staticmethod(edb)
    
    def wappAuth(appKey, appSecret, options=None,*arga,**argb):
            """appAuth"""
            appKey = w.__dargArr2str(appKey);
            appSecret = w.__dargArr2str(appSecret);
            options = w.__t2options(options,arga,argb);
            if(appKey==None or appSecret==None or options==None):
                print('Invalid arguments!');
                return;

            out =w.WindData();
            apiout=w.c_wappAuth(appKey,appSecret,options);
            out.set(apiout,1,asdate=True);
            w.c_free_data(apiout);
            
            return out;
    wappAuth=staticmethod(wappAuth)
    
    def wappMessage(type_id, message, options=None,*arga,**argb):
            """wappMessage"""
            type_id = w.__dargArr2str(type_id);
            message = w.__dargArr2str(message);
            options = w.__t2options(options,arga,argb);
            if(type_id==None or message==None or options==None):
                print('Invalid arguments!');
                return;

            out =w.WindData();
            apiout=w.c_wappMessage(type_id,message,options);
            out.set(apiout,1,asdate=True);
            w.c_free_data(apiout);
            
            return out;
    wappMessage=staticmethod(wappMessage)
    
	
    def wses(codes, fields, beginTime=None, endTime=None, options=None,*arga,**argb):
            """wses???????????"""
            if(endTime==None):  endTime = datetime.today().strftime("%Y-%m-%d")
            if(beginTime==None):  beginTime = endTime            
            codes = w.__dargArr2str(codes);
            fields = w.__dargArr2str(fields);
            options = w.__t2options(options,arga,argb);
            if(codes==None or fields==None or options==None):
                print('Invalid arguments!');
                return;
            
            if(isinstance(beginTime,date) or isinstance(beginTime,datetime)):
                beginTime=beginTime.strftime("%Y-%m-%d")

            if(isinstance(endTime,date) or isinstance(endTime,datetime)):
                endTime=endTime.strftime("%Y-%m-%d")

            out =w.WindData();
            apiout=w.c_wses(codes,fields,beginTime,endTime,options);
            out.set(apiout,1,asdate=True);
            w.c_free_data(apiout);
            
            return out;
    wses=staticmethod(wses)
	
	
    def wsee(codes, fields, options=None,*arga,**argb):
            """wsee???????????"""
            codes = w.__dargArr2str(codes);
            fields = w.__dargArr2str(fields);
            options = w.__t2options(options,arga,argb);
            if(codes==None or fields==None or options==None):
                print('Invalid arguments!');
                return;

            out =w.WindData();
            apiout=w.c_wsee(codes,fields,options);
            out.set(apiout,3);
            w.c_free_data(apiout);
            
            return out;
    wsee=staticmethod(wsee)
	
	
    def wsed(codes, fields, options=None,*arga,**argb):
            """wsed???????????"""
            codes = w.__dargArr2str(codes);
            fields = w.__dargArr2str(fields);
            options = w.__t2options(options,arga,argb);
            if(codes==None or fields==None or options==None):
                print('Invalid arguments!');
                return;

            out =w.WindData();
            apiout=w.c_wsed(codes,fields,options);
            out.set(apiout,3);
            w.c_free_data(apiout);
            
            return out;
    wsed=staticmethod(wsed)
	
def DemoWSQCallback(indata):
    """
    DemoWSQCallback ??WSQ??????????????????^?????????????w.WindData????????indata??
    ?????????C???????????????????????????????????????????????????????????

    ?????????????????????????try...except
    """
    try:
        lstr= '\nIn DemoWSQCallback:\n' + str(indata);
        print(lstr)
    except:
        return
    
def StateChangedCallback(state,reqid,errorid):
    """
    StateChangedCallback ???????dll api????????????
    ????state????????????????reqid??????????ID??errorid???????ID??
    state=1??state=2????reqid??????state=1?????????????????state=2?????????????????????????
    ?????????????reqid???????w.readdata(reqid),?????????????????????????wsq?????????????
    """
    try:
        if (state!=4):  
          global gNewDataCome
          global gFunctionDict
          
          if (state !=1) and state!=2:
              return 0;
          
          out = w.readdata(reqid);
          if(out.StateCode==0):out.StateCode=state;
          
          gFuncDictMutex.acquire();
          f=gFunctionDict[reqid];
          if(state==2):
              del(gFunctionDict[reqid])
          gFuncDictMutex.release();

          if callable(f):
              f(out);
          else:
              print(out);
          return 0;
        else:
          global gTradeFunctionDict
          out = w.readdata(reqid,0);
          f=None;
          gTradeFuncMutex.acquire();
          if( reqid in gTradeFunctionDict ):
            f=gTradeFunctionDict[reqid];
          elif( 0 in gTradeFunctionDict ):
            f=gTradeFunctionDict[0];
          gTradeFuncMutex.release();
          
          if callable(f):
            f(out);
          else:
            print(out);
          return 0;
        
    except:
        print('except');
        return 0;

gStateCallback=c_StateChangedCallbackType(StateChangedCallback)        
w.c_setStateCallback(gStateCallback);


