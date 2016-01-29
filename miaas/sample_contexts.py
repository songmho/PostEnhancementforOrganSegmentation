default_session = {
    'session_id': 1234,
    'session_start': '2016/01/27 14:06:33',
    'user_info': {
        'id': 'hanterkr',
        'user_name': 'Hanter Jung',
        'user_type': 'patient',
    }
}

default_context = {
    'session': default_session,
}

archive_context = {
    'session': default_session,
    'archive': {
        'image_list': [{
                'date': '2015/01/28',
                'subject': 'My First Heart Treatment',
                'type': 'ECG',
                'interpretations': '-',
            }, {
                'date': '2015/01/24',
                'subject': 'My First CT Image',
                'type': 'CT',
                'interpretations': '2 interpretations',
            }, {
                'date': '2015/01/02',
                'subject': 'My First X-ray',
                'type': 'X-ray',
                'interpretations': '-',
            }, {
                'date': '2014/11/17',
                'subject': 'My 2014 Brain',
                'type': 'EEG',
                'interpretations': '3 interpretations',
            }, {
                'date': '2014/08/29',
                'subject': 'My Muscle is Good, Haha!',
                'type': 'EMG',
                'interpretations': '1 interpretations',
            }],
        'image_count': 34
    },
}
