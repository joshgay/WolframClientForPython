# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals
import logging
import unittest
from wolframclient.logger.utils import setup_logging_to_file
from wolframclient.language import wl
from wolframclient.utils.tests import TestCase as BaseTestCase
from wolframclient.utils import six
if not six.JYTHON:
    from wolframclient.evaluation import WolframLanguageSession


setup_logging_to_file('/tmp/python_testsuites.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)


@unittest.skipIf(six.JYTHON, "Not supported in Jython.")
class TestCaseSettings(BaseTestCase):
    KERNEL_PATH = '/Applications/Wolfram Desktop.app/Contents/MacOS/WolframKernel'

    @classmethod
    def setUpClass(cls):
        cls.setupKernelSession()

    @classmethod
    def tearDownClass(cls):
        cls.tearDownKernelSession()

    @classmethod
    def tearDownKernelSession(cls):
        if cls.kernel_session is not None:
            cls.kernel_session.terminate()

    @classmethod
    def setupKernelSession(cls):
        cls.kernel_session = WolframLanguageSession(
            cls.KERNEL_PATH, log_kernel=False)
        cls.kernel_session.set_parameter('STARTUP_READ_TIMEOUT', 2)
        cls.kernel_session.set_parameter('TERMINATE_READ_TIMEOUT', 3)
        cls.kernel_session.start()

class TestCase(TestCaseSettings):
    def test_evaluate_basic_inputform(self):
        res = self.kernel_session.evaluate('1+1')
        self.assertEqual(res.get(), b'2')

    def test_evaluate_basic_wl(self):
        res = self.kernel_session.evaluate(wl.Plus(1, 2))
        self.assertEqual(res.get(), b'3')

    def test_evaluate_variable_updates(self):
        self.kernel_session.evaluate('ClearAll[x]; x=1')
        self.kernel_session.evaluate('x++')
        res = self.kernel_session.evaluate('x+=10')
        self.assertEqual(res.get(), b'12')

    def test_evaluate_variable_context(self):
        self.kernel_session.evaluate('ClearAll[x]; x[] := foo')
        res = self.kernel_session.evaluate('Context[x]')
        self.assertEqual(res.get(), b'"Global`"')
        res = self.kernel_session.evaluate('Context[info]')
        self.assertEqual(res.get(), b'"Global`"')

    def test_malformed_expr(self):
        res = self.kernel_session.evaluate('Range[5')
        self.assertTrue(res.success)
        self.assertEqual(res.get(), b'$Failed')

    @unittest.skipIf(six.PY2, "No async call on Python2.")
    def test_evaluate_async(self):
        future1 = self.kernel_session.evaluate_async('3+4')
        future2 = self.kernel_session.evaluate_async('10+1')
        future3 = self.kernel_session.evaluate_async('100+1')
        self.assertEqual(future1.result().get(), b'7')
        self.assertEqual(future2.result().get(), b'11')
        self.assertEqual(future3.result().get(), b'101')
