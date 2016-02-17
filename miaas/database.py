from miaas.models import *

def check_user_id(user_id):
    res = User.objects.all()
    print(res)


def insert_patient(**kwargs):
    pass


if __name__ == '__main__':
    check_user_id(12)
    pass
