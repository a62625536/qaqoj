# QAQ_OJ 配置说明

- 安装 Ubuntu 16.04 LTS 64位操作系统

- 安装mysql

```
sudo apt-get install mysql-server mysql-client
```

- 解决mysql中文乱码问题

打开mysl配置文件
```
sudo gedit /etc/mysql/my.cnf
```
在文件末尾加入以下语句
```
[client]
default-character-set=utf8
[mysqld]
character-set-server=utf8
collation-server=utf8_general_ci
init-connect='SET NAMES utf8'
```
重启mysql服务器
```
service mysql restart
```
重新打开命令行终端

- 安装virtualenv

```
sudo apt-get install virtualenv
```

- 创建Python虚拟环境

```
cd qaqoj/
virtualenv . -p python3
```

- 进入虚拟环境
```
source bin/activate
```

- 安装配置的库

```
pip install -r requirements.txt 
sudo apt-get install redis-server
```

- 安装Lorun
```
cd Lo-runner/
python setup.py install
cd ..
```

- 配置Django数据库选项

打开配置文件
```
gedit qaqoj/settings.py
```
找到以下语句
```
DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'NAME': 'mysql',
        'USER': 'root',
        'PASSWORD': '*******',
    }
}
```
用mysql的root账户的密码替换*

- 迁移数据库表单
```
python manage.py migrate
```

- 导入已有的公告和题库
```
python manage.py loaddata announcement.json
python manage.py loaddata problem.json
```

- 创建QAQ_OJ超级管理员
```
python manage.py createsuperuser
```

- 开启Django服务器
```
python manage.py runserver 0.0.0.0:端口号
```

- 开启评测服务

新开一个命令行终端，进入虚拟环境，开启评测服务
```
cd qaqoj/
source bin/activate
celery -A qaqoj worker --concurrency=1 -l info
```

- 关闭服务器

在两个终端CTRL+C




