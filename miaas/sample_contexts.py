default_session = {
    'session_id': 1234,
    'session_start': '2016/01/27 14:06:33',
    'user_info': {
        'id': 'hanterkr',
        'user_name': 'Hanter Jung',
        'user_type': 'patient',
        # 'user_type': 'physician',
    }
}

default_physician_session = {
    'session_id': 1234,
    'session_start': '2016/01/27 14:06:33',
    'user_info': {
        'id': 'hanterkr',
        'user_name': 'Hanter Jung',
        'user_type': 'physician',
    }
}

default_context = {
    'session': default_session,
}

default_physician_context = {
    'session': default_physician_session,
}

archive_context = {
    'session': default_session,
    'archive': {
        'image_list': [{
                'id': 4,
                'date': '2015/01/28',
                'subject': 'My First Heart Treatment',
                'type': 'ECG',
                'interpretations': '-',
            }, {
                'id': 3,
                'date': '2015/01/24',
                'subject': 'My First CT Image',
                'type': 'CT',
                'interpretations': '2 interpretations',
            }, {
                'id': 2,
                'date': '2015/01/02',
                'subject': 'My First X-ray',
                'type': 'X-ray',
                'interpretations': '-',
            }, {
                'id': 1,
                'date': '2014/11/17',
                'subject': 'My 2014 Brain',
                'type': 'EEG',
                'interpretations': '3 interpretations',
            }, {
                'id': 0,
                'date': '2014/08/29',
                'subject': 'My Muscle is Good, Haha!',
                'type': 'EMG',
                'interpretations': '1 interpretations',
            }],
        'image_count': 34
    },
}

    # status code
    # 0: 'Interpreted',
    # 1: 'Waiting Interpretation',
    # 2: 'Candidate Waiting',
    # 3: 'Finding Physician',
interpret_context = {
    'session': default_session,
    'interpret': {
        'interpret_list': [{
                'id': 5,
                'upload_date': '2015/01/27',
                'interpret_date': '-',
                'subject': 'My Second Muscle..',
                'type': 'EMG',
                'level': '2',
                'summary': '-',
                'status': '1',
            }, {
                'id': 4,
                'upload_date': '2015/01/24',
                'interpret_date': '-',
                'subject': 'My First CT Image',
                'type': 'CT',
                'level': '3',
                'summary': '-',
                'status': '2',
            }, {
                'id': 3,
                'upload_date': '2015/01/24',
                'interpret_date': '2015/01/28',
                'subject': 'My First CT Image',
                'type': 'CT',
                'level': '1',
                'summary': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce nec sodales odio.',
                'status': '0',
            }, {
                'id': 2,
                'upload_date': '2014/11/27',
                'interpret_date': '-',
                'subject': 'My 2014 Brain',
                'type': 'EEG',
                'level': '3',
                'summary': '-',
                'status': '3',
            }, {
                'id': 1,
                'upload_date': '2014/11/17',
                'interpret_date': '2014/12/02',
                'subject': 'My 2014 Brain',
                'type': 'EEG',
                'level': '1',
                'summary': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam congue diam eget semper elementum. Nam non purus dictum, pharetra.',
                'status': '0',
            }, {
                'id': 0,
                'upload_date': '2014/08/29',
                'interpret_date': '2014/08/30',
                'subject': 'My Muscle is Good, Haha!',
                'summary': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam pretium elit.',
                'level': '2',
                'type': 'EMG',
                'status': '0',
            }],
        'interpret_count': 67
    },
}

interpret_search_context = {
    'session': default_physician_session,

}

interpret_physician_context = {
    'session': default_physician_session,

}