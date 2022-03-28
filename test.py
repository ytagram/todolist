import unittest
import main
import json


class creditTestCase(unittest.TestCase):
    def setUp(self):
        self.hcm = self.getHCMTestCase()

    def tearDown(self):
        self.args = None

    # get hcm test data
    def getHCMTestCase(self):
        with open("testCase.json") as file:
            data = json.load(file)
        return data['hcm']

    def test_hcm(self):
        testCases = self.hcm
        for test in testCases:
            expected = test['result']
            lessonData = test['data']
            lessonCodes = list(lessonData.keys())
            HCMcounter = main.hcmCount(lessonData, lessonCodes)
            result = HCMcounter.count_hcm_credit()
            # remove blank for test
            expected = expected.replace(' ', '')
            # remove blank and break line for test
            result = result.replace(' ', '').replace("\n", '')
            self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()