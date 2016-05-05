CODE_SUCCESS = {"code": "SUCCESS"}
CODE_FAILURE = {"code": "FAILURE"}

CNT_CONTENTS_IN_PAGE = 10

INTPRT_STATUS = {
    3: 'Finding Physician',
    2: 'Candidate Waiting',
    1: 'Waiting Interpretation',
    0: 'Interpreted',
}

LEVEL_STRING = {
    1: 'Level 1 - By Software, Free of Charge, No Legal Liability',
    2: 'Level 2 - Detailed, Only with available images and profiles, Fee-based',
    3: 'Level 3 - Detailed, With available images and patient interview/symptom, Fee-based'
}

# ARCHIVE_BASE_PATH = '/Volumes/Data/archive/'
ARCHIVE_BASE_PATH = './medical_images/archive/'
TEMP_UPLOAD_DIR = './medical_images/temp/upload/'
TEMP_EXTRACT_DIR = './medical_images/temp/extract/'

CSV_ERROR_FORMAT_STRING = '<br/><br/><strong>Note. </strong>MIAAS supports various format of csv files. Nonetheless, our recommending csv file\'s row format likes: <br/>' \
                          '&nbsp;&nbsp;&nbsp;- <i><strong>Header(first) row</strong>: "(countLabel,) timeLabel, valueLabel1, valueLabel2, ..."</i> <br/>' \
                          '&nbsp;&nbsp;&nbsp;- <i><strong>Value rows</strong>: "(countValue,) time, value1, value2, ..."</i> <br/>' \
                          'In case of different format, on some occasions, MIAAS may not support a different formatted file. ' \
                          'If you can\'t upload your csv file, please check the format of the csv file.'

class PatientProfile:
    pass

class PhysicianProfile:
    pass

