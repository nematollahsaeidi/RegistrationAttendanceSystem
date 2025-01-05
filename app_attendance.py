import configparser
import os
import jdatetime
import textwrap
from flask import Flask, request, redirect, url_for, render_template, jsonify, session
import numpy as np
from datetime import date, datetime
from elasticsearch import Elasticsearch
import elasticsearch.helpers

config = configparser.ConfigParser()
config.read('cfg/config.cfg')

proxy = 'http://172.16.107.134:3128'
static_folder = './static'

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0   # add 18
app.secret_key = config.get('settings', 'secret_key')
app.config['MAX_CONTENT_LENGTH'] = int(config.get('settings', 'MAX_CONTENT_LENGTH'))


@app.route('/')
def upload_form():
    # if session.get('str_date', None) is None:
    str_date = datetime.today().date()
    fih_date = datetime.today().date()
    session['str_date'] = str_date
    session['fih_date'] = fih_date
    # else:
    return render_template('master_page_attendance.html', str_date=str_date, fih_date=fih_date)


@app.route('/', methods=['POST'])
def search_user():
    user_id = request.form['user_id']
    start_time = request.form['start_time']
    finish_time = request.form['finish_time']
    start_date = request.form['start_date']
    finish_date = request.form['finish_date']

    # session['str_date_2'] = start_date
    # session['fih_date_2'] = finish_date
    # str_date = session.get('str_date', None)
    # fih_date = session.get('fih_date', None)

    info_number, info_date, info_image, info_time, location_images, date_time_valid = search_user_date_time(user_id,
                                                                                                            start_time,
                                                                                                            finish_time,
                                                                                                            start_date,
                                                                                                            finish_date)
    # info_id = [3889, 3512] 2 4
    # info_date = ['2020-12-12', '2020-12-12']
    # info_time = ['013301', '013302']
    # info_image = ['014320.jpg', '014352.jpg']
    # location_images = ['/20201212/014848']

    # convert Gregorian date to Persian date
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

    # test time is valid
    date_time_valid = True
    if start_date_time > finish_date_time:
        date_time_valid = False

    # start_date_time = str(start_date_time).replace(' ', 'T')
    # finish_date_time = str(finish_date_time).replace(' ', 'T')

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
    dataset_dir = '/'
    detected_date = []
    detected_time = []
    time_changes = []
    location_images = []
    time_changes_1 = []
    date_changes_1 = []
    date_changes_2 = []

    for hit in res:
        record = hit["_source"]
        # try:
        #     if iteration < 9_999:
        dataset_id.append(record['personId'])
        dataset_detected_time.append(record['detectedTime'])
        # print(dataset_id)
        # print(dataset_detected_time)
        good_samples += 1
        iteration += 1
        # print(iteration)
        # else:
        #     break
        # except:
        #     pass

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
        # hour, minute, sec = textwrap.wrap(time_person, 2)
        location_images.append(os.path.join(dataset_dir, date_changes_1, name_image))
    return dataset_id, date_changes_2, detected_time, time_changes_1, location_images, date_time_valid


@app.route('/display/<filename>')
def display_image(filename):
    filename = os.path.join('/20201212/', filename)
    return redirect(url_for('static', filename=filename), code=301)


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0', port='5004', threaded=False)