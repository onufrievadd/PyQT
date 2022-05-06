import sys
sys.path.append('../')
from client import create_presence, process_response_ans
from common.variables import *
import unittest
from errors import ReqFieldMissingError, ServerError


# Класс с тестами
class TestClass(unittest.TestCase):
    def test_def_presense(self):
        test = create_presence('Guest')
        test[TIME] = 1.1
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_200_ans(self):
        self.assertEqual(process_response_ans({RESPONSE: 200}), '200 : OK')

    def test_400_ans(self):
        self.assertRaises(ServerError, process_response_ans , {RESPONSE: 400, ERROR: 'Bad Request'})

    def test_no_response(self):
        self.assertRaises(ReqFieldMissingError, process_response_ans, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
