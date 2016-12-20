============================================================
	目录结构说明
============================================================
blog			工程APP
blog_test		工程主目录
templates		工程使用的各模板文件

manage.py		工程主控工具脚本


============================================================
	环境安装说明
============================================================
1. 安装Python
（1）执行 python-2.7.12.amd64.msi 默认安装
（2）注册环境变量PATH:以添加python执行程序路径

2. 安装Django
（1）将Django-1.10.4.tar.gz解压到python安装目录下
（2）进入Django-1.10.4文件夹下，执行python setup.py install

============================================================
	工具部署说明
============================================================
1. 修改 blog_test\blog_test\urls.py文件第29行，以指向本机templates目录（注意斜线方向）
{'document_root': 'C:\Users\chen.xiaohong\djangowork\blog_test\templates'}),
 

2. 修改 blog_test\blog_test\setting.py文件第59行，以指向本机templates目录
'DIRS': ['C:/Users/chen.xiaohong/djangowork/blog_test/templates'],


============================================================
	工具使用说明
============================================================
1. 于cmd命令行，进入blog_test工作目录，以主控脚本启动
python manager.py runserver 

2. 测试页面访问

http://127.0.0.1:8000/
http://127.0.0.1:8000/search
http://127.0.0.1:8000/account/login

