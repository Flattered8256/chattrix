# 一款完全开源的web即时通讯软件

## 安装教程
1. 拉取代码到本地仓库：git clone https://github.com/Flattered8256/chattrix.git
2. 配置域名：vim chattrix/django/chattrix/settings.py，把CSRF_TRUSTED_ORIGINS = ['http://www.chattrix.com', 'https://www.chattrix.com']中的域名替换成实际的域名，有端口号要加端口，比如http://www.chattrix.com:3000
3. 切换到docker-compoes.yml所在的路径，并执行docker-compose up -d构建


## 后台管理
1.创建管理员账号：docker exec -it chattrix_backend python manage.py createsuperuser
2.在主网址后面加/admin即可进入后台管理页面
 
