"""
Date: 2019. 11. 08
Programmer: MH
Description: generate random string for invitation code
"""

import random
import string


class InvitationCodeGenerator:
    """
    Class for generating inviting code
    """
    def __init__(self, size=6, chars=string.ascii_uppercase+string.ascii_letters+string.digits):
        """
        To initialize variables
        :param size: int, # of characters in the code
        :param chars: list, list of candidate character
        :return:
        """
        self.chars = chars
        self.size = size
        self.created_code = None

    def get_invitation_code(self, list_made=[]):
        """
        To return invitation code not to overlapped
        :param list_made: list, list of invitation code already made
        :return: sting, new intivation code
        """
        self.created_code = ""
        while True:
            self.created_code = "".join(random.choice(self.chars) for x in range(self.size))
            if self.created_code not in list_made:
                return self.created_code


if __name__ == '__main__':
    icg = InvitationCodeGenerator(size=6, chars=string.ascii_uppercase+string.ascii_lowercase+string.digits)
    print(string.ascii_uppercase+string.ascii_lowercase+string.digits)
    print(len(string.ascii_uppercase+string.ascii_lowercase+string.digits))
    for i in range(30):
        print(icg.get_invitation_code())
