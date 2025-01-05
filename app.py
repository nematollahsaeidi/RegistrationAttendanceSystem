import jdatetime
from datetime import date, datetime
import elasticsearch.helpers
import configparser
import requests
import os
import json
from flask import Flask, request, redirect, url_for, render_template, jsonify, session

config = configparser.ConfigParser()
config.read('cfg/config.cfg')

proxy = 'http://172.16.107.134:3128'
static_folder = './static'

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # add 18
app.secret_key = config.get('settings', 'secret_key')
app.config['MAX_CONTENT_LENGTH'] = int(config.get('settings', 'MAX_CONTENT_LENGTH'))
app.secret_key = config.get('settings', 'secret_key')
token = config.get('path', 'PODSPACE_TOKEN')
podspace_download_url = config.get('path', 'PODSPACE_DOWNLOAD_URL')
podspace_upload_url = config.get('path', 'PODSPACE_UPLOAD_URL')
upload_folder = config.get('path', 'UPLOAD_FOLDER')
payload_filename = config.get('path', 'payload_filename')


@app.route('/')
def upload_form():
    return render_template('base.html', flag=False)


# app attendance
@app.route('/attendance')
def upload_form_attendance():
    str_date = datetime.today().date()
    fih_date = datetime.today().date()
    session['str_date'] = str_date
    session['fih_date'] = fih_date
    return render_template('master_page_attendance.html', str_date=str_date, fih_date=fih_date)


@app.route('/attendance', methods=['POST'])
def search_user():
    user_id = request.form['user_id']
    start_time = request.form['start_time']
    finish_time = request.form['finish_time']
    start_date = request.form['start_date']
    finish_date = request.form['finish_date']

    info_number, info_date, info_image, info_time, location_images, date_time_valid = search_user_date_time(user_id,
                                                                                                            start_time,
                                                                                                            finish_time,
                                                                                                            start_date,
                                                                                                            finish_date)
    info_date_persian = []
    for i in info_date:
        date_time_persian = jdatetime.date.fromgregorian(day=int(i.split('-')[2]),
                                                         month=int(i.split('-')[1]),
                                                         year=int(i.split('-')[0]))
        date_time_persian_join = '-'.join([str(date_time_persian.year), str(date_time_persian.month),
                                           str(date_time_persian.day)])
        info_date_persian.append(date_time_persian_join)

    return render_template('master_page_attendance.html', info_number=info_number,
                           info_date=info_date_persian,
                           info_image=info_image, info_image_time=info_time, location_images=location_images,
                           str_date=start_date, fih_date=finish_date, date_time_valid=date_time_valid)


def search_user_date_time(user_id, start_time, finish_time, start_date, finish_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    finish_date = datetime.strptime(finish_date, '%Y-%m-%d').date()
    start_time = datetime.strptime(start_time, '%H:%M').time()
    finish_time = datetime.strptime(finish_time, '%H:%M').time()
    start_date_time = datetime.combine(start_date, start_time)
    finish_date_time = datetime.combine(finish_date, finish_time)

    date_time_valid = True
    if start_date_time > finish_date_time:
        date_time_valid = False

    es = elasticsearch.Elasticsearch(
        [config.get('elastic', 'ip')],
        http_auth=(config.get('elastic', 'user'), config.get('elastic', 'password')),
        scheme=config.get('elastic', 'scheme'),
        port=int(config.get('elastic', 'port')))
    if len(user_id) == 0:
        res = elasticsearch.helpers.scan(
            es,
            query={"query": {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "detectedTime": {
                                    "gte": start_date_time,
                                    "lte": finish_date_time
                                }
                            }
                        }
                    ]
                }
            }
            },
            index=config.get('elastic', 'base_index')
            # size=,
            # doc_type='',
            # preserve_order=True
        )
    else:
        res = elasticsearch.helpers.scan(
            es,
            query={"query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "personId": user_id
                            }
                        }
                    ],
                    "filter": [
                        {
                            "range": {
                                "detectedTime": {
                                    "gte": start_date_time,
                                    "lte": finish_date_time
                                }
                            }
                        }
                    ]
                }
            }
            },
            index=config.get('elastic', 'base_index')
            # size=,
            # doc_type='',
            # preserve_order=True
        )

    iteration = 0
    good_samples = 0
    dataset_id = []
    dataset_detected_time = []
    dataset_dir = '/'  ################dfg
    detected_date = []
    detected_time = []
    time_changes = []
    location_images = []
    time_changes_1 = []
    date_changes_1 = []
    date_changes_2 = []

    for hit in res:
        record = hit["_source"]
        dataset_id.append(record['personId'])
        dataset_detected_time.append(record['detectedTime'])
        good_samples += 1
        iteration += 1

    for item in dataset_detected_time:
        date_change = item.split('T')[0]
        date_changes_2.append(date_change)
        date_changes_1 = date_change.replace('-', '')
        detected_date.append(date_changes_1)
        time_change = item.split('T')[1].split('.')[0]
        time_changes_1.append(time_change)
        time_change_2 = time_change.replace(':', '')
        name_image = time_change_2 + '.jpg'
        time_changes.append(time_change_2)
        detected_time.append(time_change_2 + '.jpg')
        location_images.append(os.path.join(dataset_dir, date_changes_1, name_image))
    return dataset_id, date_changes_2, detected_time, time_changes_1, location_images, date_time_valid


@app.route('/display/<filename>')
def display_image(filename):
    filename = os.path.join('/20201212/', filename)
    return redirect(url_for('static', filename=filename), code=301)


# app data register
@app.route('/register')
def upload_form_register():
    return render_template('master_data_register.html', flag=False)


@app.route('/register', methods=['POST'])
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
            output_message_video = json.loads(request_receive_video.text)['message']
            if type(output_message_video) is dict:
                array_select = [output_message_video]
                output_message_video = array_select
            output_status_video = request_receive_video.status_code
        flag_video = True
    return render_template('master_data_register.html', flag=flag, output_message_video=output_message_video,
                           output_status_video=output_status_video, output_message_zip=output_message_zip,
                           output_status_zip=output_status_zip, uploaded_url=uploaded_url, user_id=user_id,
                           flag_video=flag_video, flag_zip=flag_zip)


def request_receive(user_id, uploaded_url):
    headers = {'Content-type': 'application/json; charset=utf-8'}
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
