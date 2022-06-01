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
    sql = "Select anomalous_event_type, risk_type, anomalous_event_id from anomalous_event_data"
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
        anomalous_event_dic = {}
        for i in range (len(data)):
            anomalous_event_dic[data[i][0]] = [data[i][1], data[i][2]]
    except Exception as e:
        db.rollback()  # 如果出错就会滚数据库并且输出错误信息。
        print("Error:{0}".format(e))

    sql = "Select area_name, area_id from area_data"
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
    return anomalous_event_dic, area_dic #返回结果为两个字典（key事件类型 ： val对应编号）

def main(person_id):
    anomalous_event_dic, area_dic = get_data()

    risk = input_group("请输入报警信息", [
        select(name = "area", label='请选择区域', options=area_dic.keys()),
        select(name = "anomalous_event", label='请选择事故', multiple=True, required = True, options=anomalous_event_dic.keys()),
    ])

    anomalous_risk_id = []
    anomalous_event_id = []
    anomalous_event_name = []
    for i in range(len(risk["anomalous_event"])):
        anomalous_risk_id.append(anomalous_event_dic[risk["anomalous_event"][i]][0])
        anomalous_event_id.append(anomalous_event_dic[risk["anomalous_event"][i]][1])
        anomalous_event_name.append(risk["anomalous_event"][i])
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db(now, anomalous_risk_id, anomalous_event_id, area_dic[risk["area"]], person_id)
    put_table([
        [area_dic[risk["area"]], risk["area"], anomalous_risk_id, anomalous_event_id, anomalous_event_name, now, person_id]],
        header=["地点ID", "地点", "报警ID", "事件ID", "事件类型", "时间", "人员ID"])
    confirm = actions('', ['继续上报', '重新选择上报内容'], help_text='')
    if confirm == '继续上报':
        clear()
        main(person_id)
    else:
        clear()
        index.main()
    return

def db(now, anomalous_risk_id, anomalous_event_id, area_id, person_id): #写入数据库
    try:
        db = pymysql.connect(host="10.255.51.168", user="root", password="159357", database="test", port=3306, charset='utf8')
    except pymysql.Error as e:
        print("数据库连接失败：" + str(e))
    cursor = db.cursor()
    for i in range (len(anomalous_event_id)):
        sql = "Insert into risk_time_area_data (time, risk_id, anomalous_event_id,area_id, person_id) values ('%s', %d, %d, %d,'%s')" \
              %(now, anomalous_risk_id[i], anomalous_event_id[i], area_id, person_id)
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            db.rollback()  # 如果出错就会滚数据库并且输出错误信息。
            print("Error:{0}".format(e))
    db.close()  # 关闭数据库


if __name__ == "__main__":
    start_server(main, port=8080, debug=True,cdn=False)


