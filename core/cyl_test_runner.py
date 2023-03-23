import logging
import time
from abc import ABC, abstractmethod
from typing import final

from .cyl_util import fail_sign, success_sign

mylogger = logging.getLogger(__name__)
mylogger.setLevel(logging.DEBUG)

class CYLTestCase(ABC):

    def __init__(self, test_alias: str, **kwargs):
        self.alias = test_alias
        self.input = kwargs

    @abstractmethod
    def run(self, **kwargs):
        print(self.input)
        return (True, "pass")


class CYLTestRunner(ABC):

    def __init__(self):
        self._test_list = list()
        self.fail_counter = 0
        self.result_dict = dict()
        pass

    @abstractmethod
    def setup(self):
        return True, "PASS"

    @abstractmethod
    def tearDown(self):
        return True, "PASS"

    @final
    def addTest(self, test_object):
        self._test_list.append(test_object)

    @final
    def execute(self):

        ## setup
        ret, out = self.setup()
        self.result_dict["setup"] = {"result": ret, "out": out}

        if ret is False:
            return False, self.result_dict

        ## execute case
        self.result_dict["cases"] = {}
        number_cases = len(self._test_list)
        self.result_dict["number of cases"] = number_cases
        for test in self._test_list:
            # print("Alias:", test.alias)
            mylogger.info(f"<{test.alias}> Start Test.")
            start_time = time.time()
            ret, out = test.run()
            time_spent = time.time() - start_time
            self.result_dict["cases"][test.alias] = {"result": ret, "out": out, "time spent": time_spent}
            
            if ret == False:
                self.fail_counter += 1
                mylogger.warning(f"<{test.alias}> Failed! Message: {out}")
                mylogger.warning(fail_sign)
            else:
                mylogger.info(f"<{test.alias}> Success! Message: {out}")
                mylogger.info(success_sign)
        
        mylogger.info(f"Test Result: {number_cases-self.fail_counter}/{number_cases} Success!")
        self.result_dict["failure rate"] = f"{(self.fail_counter*100/number_cases)}%"

        ## tearDown
        ret, out = self.tearDown()
        self.result_dict["tearDown"] = {"result": ret, "out": out}
        if ret is False:
            return False, self.result_dict

        return self.fail_counter==0, self.result_dict

