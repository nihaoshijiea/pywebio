import pymysql as pymysql
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from pywebio import start_server
from pywebio.session import *
import pandas as pd
import time
import datetime
import pymysql
import index

def get_data(): #从excel表中读取事件和地区以及对应的ID
    try:
        db = pymysql.connect(host="10.255.51.168", user="root", password="159357", database="test", port=3306, charset='utf8')
    except pymysql.Error as e:
        print("数据库连接失败：" + str(e))
    cursor = db.cursor()
    sql = "Select equipment_id, equipment_type, area_id from equipment_data"
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
        equipment_dic = {}
        for i in range (len(data)):
            equipment_dic[data[i][0]] = [data[i][1], data[i][2]]
    except Exception as e:
        db.rollback()  # 如果出错就会滚数据库并且输出错误信息。
        print("Error:{0}".format(e))

    sql = "Select area_id, area_name from area_data"
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
        area_dic = {}
        for i in range (len(data)):
            area_dic[data[i][0]] = data[i][1]
    except Exception as e:
        db.rollback()
        print("Error:{0}".format(e))
    db.close()  # 关闭数据库
    return equipment_dic, area_dic#返回结果为两个字典（key事件类型 ： val对应编号）

def main(person_id):
    equipment_dic, area_dic = get_data()

    def check_ID(ID):
        if ID > len(equipment_dic) or ID < 0:
            return '您的输入有问题'

    info = input_group("请输入设备信息", [
        input('请输入设备ID', type=NUMBER, name='equipment_id', required=True, validate=check_ID),
    ])

    equipment_id = info["equipment_id"]
    equipment_type = equipment_dic[equipment_id][0]
    area_id = equipment_dic[equipment_id][1]
    area_type = area_dic[area_id]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    put_table([
        [area_id, area_type, equipment_id, equipment_type, now, person_id]],
        header=["地点ID", "地点", "设备ID", "设备类型", "时间", "人员ID"])

    if equipment_type == '灭火瓶':
        info = input_group("请输入检查结果", [
            select(label='是否可用', name="use_double", options=['是','否']),
            input(label='保质日期(年-月-日)', type=TEXT, name='quality_guarantee_period', required=True),
        ])
        if info["use_double"] == "是":
            use_double = 1
        else:
            use_double = 0
        quality_guarantee_period = info["quality_guarantee_period"]
        put_table([
            [info["use_double"], quality_guarantee_period]],
            header=["是否可用", "保质日期"])
        put_db(equipment_id, equipment_type, use_double, quality_guarantee_period, -1, -1, now, person_id)
    elif equipment_type == '消防通道':
        info = input_group("请输入检查结果", [
            select(label='是否可用', name="use_double", options=['是', '否']),
            select(label='是否堵塞', name="block", options=['是', '否']),
        ])
        if info["use_double"] == "是":
            use_double = 1
        else:
            use_double = 0
        if info["block"] == "是":
            block = 1
        else:
            block = 0
        put_table([
            [info["use_double"], info["block"]]],
            header=["是否可用", "是否堵塞"])
        put_db(equipment_id, equipment_type, use_double, -1, block, -1, now, person_id)
    elif equipment_type == '水泵':
        info = input_group("请输入检查结果", [
            select(label='是否可用', name="use_double", options=['是', '否']),
            input(label='水压大小', type=TEXT, name='hydraulic_pressure', required=True),
        ])
        if info["use_double"] == "是":
            use_double = 1
        else:
            use_double = 0
        hydraulic_pressure = int (info["hydraulic_pressure"])
        put_table([
            [info["use_double"], info["hydraulic_pressure"]]],
            header=["是否可用", "水压大小"])
        put_db(equipment_id, equipment_type, use_double, -1, -1, hydraulic_pressure, now, person_id)
    else:
        info = input_group("请输入检查结果", [
            select(label='是否可用', name="use_double", options=['是', '否']),
        ])
        if info["use_double"] == "是":
            use_double = 1
        else:
            use_double = 0
        put_table([
            [info["use_double"]]],
            header=["是否可用"])
        put_db(equipment_id, equipment_type, use_double, -1, -1, -1, now, person_id)

    confirm = actions('', ['继续上报', '重新选择上报内容'], help_text='')
    if confirm == '继续上报':
        clear()
        main(person_id)
    else:
        clear()
        index.main()
    return

def put_db(equipment_id, equipment_type, use_double, quality_guarantee_period, block, hydraulic_pressure, now, person_id): #写入数据库
    try:
        db = pymysql.connect(host="10.255.51.168", user="root", password="159357", database="test", port=3306, charset='utf8')
    except pymysql.Error as e:
        print("数据库连接失败：" + str(e))
    cursor = db.cursor()
    if equipment_type == '灭火瓶':
        sql = "Replace into equipment_state_data (equipment_id, equipment_type, use_double, quality_guarantee_period, ntime, person_id) values (%d, '%s', %d,'%s','%s','%s')" \
              % (equipment_id, equipment_type, use_double, quality_guarantee_period, now, person_id)
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            db.rollback()  # 如果出错就会滚数据库并且输出错误信息。
            print("Error:{0}".format(e))
    elif equipment_type == '消防通道':
        sql = "Replace into equipment_state_data (equipment_id, equipment_type, use_double, block, ntime, person_id) values (%d, '%s', %d, %d,'%s','%s')" \
              % (equipment_id, equipment_type, use_double, block, now, person_id)
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            db.rollback()  # 如果出错就会滚数据库并且输出错误信息。
            print("Error:{0}".format(e))
    elif equipment_type == '水泵':
        sql = "Replace into equipment_state_data (equipment_id, equipment_type, use_double, hydraulic_pressure, ntime, person_id) values (%d, '%s', %d,%d,'%s','%s')" \
              % (equipment_id, equipment_type, use_double, hydraulic_pressure, now, person_id)
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            db.rollback()  # 如果出错就会滚数据库并且输出错误信息。
            print("Error:{0}".format(e))
    else:
        sql = "Replace into equipment_state_data (equipment_id, equipment_type, use_double, ntime, person_id) values (%d, '%s', %d,'%s', '%s')" \
              % (equipment_id, equipment_type, use_double, now, person_id)
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            db.rollback()  # 如果出错就会滚数据库并且输出错误信息。
            print("Error:{0}".format(e))
    db.close()  # 关闭数据库


if __name__ == "__main__":
    start_server(main, port=8080, debug=True,cdn=False)


