%设置数据类型
setdbprefs('datareturnformat','cellarray');
%matlab 默认每次 fetch 取 100000 行，下面两条语句可以调整每次取多少行
%setdbprefs('FetchInBatches','yes')
%setdbprefs('FetchBatchSize','2')
%连接数据库
conn=database.ODBCConnection('t1','','');
%执行 TSL 语句
tsl_str='setsysparam(pn_stock(),"SZ000002");setsysparam(pn_date(),today());return nday(1000,"时间",datetimetostr(sp_time()), "开盘价",open(), "收盘价",close());';
curs=exec(conn, tsl_str);
%提取数据
curs=fetch(curs);
Data=curs.Data;
close(curs);
close(conn);

% %转换数据
% price=cell2mat(Data(:,2:3));
% %画图
% plot(price);
% xlabel('天');ylabel('收盘价');title('万科 A 最近 30 个交易日开盘价/收盘价');