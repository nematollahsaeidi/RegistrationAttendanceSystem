import configparser
import requests
import os
import cv2
import json
from flask import Flask, request, redirect, url_for, render_template, jsonify, session

# from config.config import configurations
# from elasticsearch import Elasticsearch
# import elasticsearch.helpers

config = configparser.ConfigParser()
config.read('cfg/config.cfg')

static_folder = './static'

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0   # add 18
app.secret_key = config.get('settings', 'secret_key')
app.config['MAX_CONTENT_LENGTH'] = int(config.get('settings', 'MAX_CONTENT_LENGTH'))
token = config.get('path', 'PODSPACE_TOKEN')
podspace_download_url = config.get('path', 'PODSPACE_DOWNLOAD_URL')
podspace_upload_url = config.get('path', 'PODSPACE_UPLOAD_URL')
upload_folder = config.get('path', 'UPLOAD_FOLDER')
payload_filename = config.get('path', 'payload_filename')


@app.route('/')
def upload_form():
    return render_template('master_data_register.html', flag=False)


@app.route('/', methods=['POST'])
def add_user():
    file_zip = request.files['file1']
    file_video = request.files['file2']
    user_id = request.form['user_id']

    file_selective_zip = None
    file_selective_video = None
    file_dir = None
    flag = True
    flag_zip = False
    flag_video = False
    output_status_video = []
    output_message_video = []
    output_status_zip = []
    output_message_zip = []
    if file_zip.filename.endswith(".zip"):
        flag = False
        file_zip.filename = str(user_id) + '_' + file_zip.filename
        file_selective_zip = file_zip
        file_dir = os.path.join(upload_folder, file_selective_zip.filename)
        file_selective_zip.save(file_dir)

        server_file_name = user_id
        uploaded_url = None
        if not flag:
            uploaded_url = upload(file_dir, server_file_name)
        headers = {'Content-type': 'application/json; charset=utf-8'}

        if file_zip.filename.endswith(".zip"):
            request_receive_zip = requests.get(url='http://10.60.110.13:4002/receiveZip', headers=headers,
                                               data=json.dumps({"zipUrl": uploaded_url, "userId": user_id,
                                                                "packetId": '1111'}))
            # request_receive_zip = requests.request("GET", url='http://10.60.110.13:4002/receiveZip', headers=headers,
            #                                        data=json.dumps(payload))
            # request_receive_zip = request_receive(user_id, uploaded_url)
            output_message_zip = json.loads(request_receive_zip.text)['message']  # +
            if type(output_message_zip) is dict:
                array_select = [output_message_zip]
                output_message_zip = array_select
            output_status_zip = request_receive_zip.status_code
        flag_zip = True

    if file_video.filename.endswith(".mp4") or file_video.filename.endswith(".MPV") or \
            file_video.filename.endswith(".MP4V-ES") or file_video.filename.endswith(".mkv") or \
            file_video.filename.endswith(".MPEG"):
        flag = False
        file_video.filename = str(user_id) + '_' + file_video.filename
        file_selective_video = file_video
        file_dir = os.path.join(upload_folder, file_selective_video.filename)
        file_selective_video.save(file_dir)
        # video_cap = cv2.VideoCapture(file_dir)

        server_file_name = user_id
        uploaded_url = None
        if not flag:
            uploaded_url = upload(file_dir, server_file_name)
        headers = {'Content-type': 'application/json; charset=utf-8'}

        if file_video.filename.endswith(".mp4") or file_video.filename.endswith(".MPV") or \
                file_video.filename.endswith(".MP4V-ES") or file_video.filename.endswith(".mkv") or \
                file_video.filename.endswith(".MPEG"):
            request_receive_video = requests.get(url='http://10.60.110.13:4002/receiveVideo', headers=headers,
                                                 data=json.dumps({"videoUrl": uploaded_url, "userId": user_id,
                                                                  "packetId": '1111'}))
            output_message_video = json.loads(request_receive_video.text)['message']  # +
            if type(output_message_video) is dict:
                array_select = [output_message_video]
                output_message_video = array_select
            output_status_video = request_receive_video.status_code
        flag_video = True
    # else:
    #     flag = True

    # server_file_name = user_id
    # uploaded_url = None
    # if not flag:
    #     uploaded_url = upload(file_dir, server_file_name)
    # output_status_video = []
    # output_message_video = []
    # output_status_zip = []
    # output_message_zip = []
    # headers = {'Content-type': 'application/json; charset=utf-8'}
    # if file_zip.filename.endswith(".zip"):
    #     request_receive_zip = requests.get(url='http://10.60.110.13:4002/receiveZip', headers=headers,
    #                                        data=json.dumps({"zipUrl": uploaded_url, "userId": user_id,
    #                                                         "packetId": '1111'}))
    #     # request_receive_zip = requests.request("GET", url='http://10.60.110.13:4002/receiveZip', headers=headers,
    #     #                                        data=json.dumps(payload))
    #     # request_receive_zip = request_receive(user_id, uploaded_url)
    #     output_message_zip = json.loads(request_receive_zip.text)['message'] #+
    #     if type(output_message_zip) is dict:
    #         array_select = [output_message_zip]
    #         output_message_zip = array_select
    #     output_status_zip = request_receive_zip.status_code
    # if file_video.filename.endswith(".mp4") or file_video.filename.endswith(".MPV") or \
    #         file_video.filename.endswith(".MP4V-ES") or file_video.filename.endswith(".mkv") or \
    #         file_video.filename.endswith(".MPEG"):
    #     request_receive_video = requests.get(url='http://10.60.110.13:4002/receiveVideo', headers=headers,
    #                                          data=json.dumps({"videoUrl": uploaded_url, "userId": user_id,
    #                                                           "packetId": '1111'}))
    #     output_message_video = json.loads(request_receive_video.text)['message'] #+
    #     if type(output_message_video) is dict:
    #         array_select = [output_message_video]
    #         output_message_video = array_select
    #     output_status_video = request_receive_video.status_code

    # return render_template('master_data_register.html', flag=flag)
    return render_template('master_data_register.html', flag=flag, output_message_video=output_message_video,
                           output_status_video=output_status_video, output_message_zip=output_message_zip,
                           output_status_zip=output_status_zip, uploaded_url=uploaded_url, user_id=user_id,
                           flag_video=flag_video, flag_zip=flag_zip)


def request_receive(user_id, uploaded_url):
    headers = {'Content-type': 'application/json; charset=utf-8'}
    # queries = open('')
    # for line in queries:
    #     payload = {
    #         "businessId": "test_biz",
    #         "packetId": "4335",
    #         "query": line,
    #         "count": "1",
    #         "userId": user_id,
    #         "offset": 0
    #     }
    payload = {"zipUrl": uploaded_url, "userId": user_id, "packetId": '1111'}
    response = requests.request("GET", url='http://10.60.110.13:4002/receiveZip', headers=headers,
                                data=json.dumps(payload))
    return response


def upload(file_name, server_file_name):
    with open(file_name, 'rb') as f:
        contents = f.read()

    payload = {'filename': payload_filename + server_file_name,  # + '.mp4',  #'.zip'
               'isPublic': True}
    headers = {
        '_token_': token,
        '_token_issuer_': '1'
    }
    files = [('file', contents)]
    uploaded_url = None
    response = requests.post(url=podspace_upload_url, headers=headers, data=payload, files=files)
    if response.status_code == 200:
        response_json = response.json()
        if not response_json['hasError']:
            hash_code = response_json['result']['hashCode']
            uploaded_url = podspace_download_url + hash_code
    return uploaded_url


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0', port='5006', threaded=False)

    # if not (file_zip.filename.endswith(".zip") or file_video.filename.endswith(".cap")):
    #     flag = True
    # else:
    #     flag = False

    # PODSPACE_TOKEN = 'a5815c166b9a494a90a5604801007795',
    # PODSPACE_DOWNLOAD_URL = "https://podspace.pod.ir/nzh/drive/downloadFile?hash=",
    # PODSPACE_UPLOAD_URL = "https://podspace.pod.ir/nzh/drive/uploadFile/",
    # conf = configurations[1]
    # token = conf['PODSPACE_TOKEN']
    # podspace_download_url = conf['PODSPACE_DOWNLOAD_URL']
    # podspace_upload_url = conf['PODSPACE_UPLOAD_URL']

    # user_id = request.form['user_id']
    # session['str_date_2'] = start_date
    # str_date = session.get('str_date', None)
    # info_number, info_date, info_image, info_time, location_images = search_user_date_time(user_id, start_time,
    #                                                                                        finish_time,
    #                                                                                        start_date,
    #                                                                                        finish_date)

    # url = 'http://192.168.3.45:8080/api/v2/event/log'
    # url = 'http://podspace.pod.ir/nzh/drive/uploadFile/'
    # headers = {'content-type': 'application/json'}
    # data = {"eventType": "AAS_PORTAL_START", "data": {"uid": "hfe3hf45huf33545", "aid": "1", "vid": "1"}}
    # params = {'sessionKey': '9ebbd0b25760557393a43064a92bae539d962103', 'format': 'xml', 'platformId': 1}
    # requests.post(url, params=params, json=data, headers=headers)
