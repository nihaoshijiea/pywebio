import pymysql as pymysql
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from pywebio import start_server


import equipment_state_data
import risk_time_area_data

def main():
    info = input_group('', [
        input('请输入您的ID', type=TEXT, name='person_id', required=True),
        actions('请选择内容?', ['上报紧急情况', '上报器材情况'], name = 'content', help_text='请谨慎选择')
    ])
    if info['content'] == "上报紧急情况":
        risk_time_area_data.main(info['person_id'])
    else:
        equipment_state_data.main(info['person_id'])
    return


if __name__ == "__main__":
    start_server(main, port=8080, debug=True,cdn=False)


