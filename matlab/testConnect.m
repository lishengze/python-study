%������������
setdbprefs('datareturnformat','cellarray');
%matlab Ĭ��ÿ�� fetch ȡ 100000 �У��������������Ե���ÿ��ȡ������
%setdbprefs('FetchInBatches','yes')
%setdbprefs('FetchBatchSize','2')
%�������ݿ�
conn=database.ODBCConnection('t1','','');
%ִ�� TSL ���
tsl_str='setsysparam(pn_stock(),"SZ000002");setsysparam(pn_date(),today());return nday(1000,"ʱ��",datetimetostr(sp_time()), "���̼�",open(), "���̼�",close());';
curs=exec(conn, tsl_str);
%��ȡ����
curs=fetch(curs);
Data=curs.Data;
close(curs);
close(conn);

% %ת������
% price=cell2mat(Data(:,2:3));
% %��ͼ
% plot(price);
% xlabel('��');ylabel('���̼�');title('��� A ��� 30 �������տ��̼�/���̼�');