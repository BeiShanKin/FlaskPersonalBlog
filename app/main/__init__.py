from flask import Blueprint
# 创建蓝图
main = Blueprint('main', __name__)

# 导入蓝图中模块
from . import views, errors
