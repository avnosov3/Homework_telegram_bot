import requests
from unittest import TestCase, mock, main as uni_main

import homework


class TestReq(TestCase):

    @mock.patch('requests.get')
    def test_server_failure(self, request_get):
        request_get.side_effect = mock.Mock(
            side_effect=requests.RequestException('testing')
        )
        homework.main()

    @mock.patch('requests.get')
    def test_server_rejects_request(self, request_get):
        JSON = {'error': 'testing'}
        resp = mock.Mock()
        resp.status_code = 200
        resp.json = mock.Mock(
            return_value=JSON)
        request_get.return_value = resp
        homework.main()

    @mock.patch('requests.get')
    def test_status_code(self, request_get):
        resp = mock.Mock()
        resp.status_code = 333
        request_get.return_value = resp
        homework.main()

    @mock.patch('requests.get')
    def test_surprizing_status_homework(self, request_get):
        JSON = {'homeworks': [{'homework_name': 'test', 'status': 'test'}]}
        resp = mock.Mock()
        resp.status_code = 200
        resp.json = mock.Mock(
            return_value=JSON)
        request_get.return_value = resp
        homework.main()
    
    @mock.patch('requests.get')
    def test_surprizing_status_homework(self, request_get):
        JSON = {'homeworks': 1}
        resp = mock.Mock()
        resp.status_code = 200
        resp.json = mock.Mock(
            return_value=JSON)
        request_get.return_value = resp
        homework.main()

uni_main()
