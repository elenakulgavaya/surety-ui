import base64

import json

from surety.diff import compare
from selenium.common.exceptions import WebDriverException

from surety.ui.browser import Browser


class Command:
    GET_ITEM = 'return window.localStorage.getItem(arguments[0]);'
    ADD_ITEM = 'window.localStorage.setItem(arguments[0], arguments[1]);'
    DELETE = 'window.localStorage.removeItem(arguments[0]);'
    CLEAR = 'window.localStorage.clear();'


class LocalStorage:
    @classmethod
    def run_command(cls, command, *args):
        return Browser().driver.execute_script(command, *args)

    @classmethod
    def get_item(cls, key):
        return cls.run_command(Command.GET_ITEM, key)

    @classmethod
    def set_item(cls, name, value):
        if not isinstance(value, (str, bool)):
            if isinstance(value, int):
                value = f'"{value}"'
            else:
                value = json.dumps(value)

        cls.run_command(Command.ADD_ITEM, name, value)

    @classmethod
    def remove_item(cls, name):
        try:
            cls.run_command(Command.DELETE, name)
        except Exception as e:  # pylint:disable=broad-except
            print("FAILED TO CLEAR STORAGE")
            print(e)

    @classmethod
    def clear(cls):
        try:
            cls.run_command(Command.CLEAR)
        except WebDriverException:
            print('Local storage is not accessible')

    @classmethod
    def set_encoded(cls, key, data):
        cls.set_item(
            key,
            base64.b64encode(json.dumps(data).encode('utf-8')).decode('utf-8')
        )

    @classmethod
    def verify_decoded(cls, key, expected_data):
        actual = cls.get_item(key)
        compare(
            expected=expected_data,
            actual=actual and json.loads(base64.b64decode(actual))
        )

    @classmethod
    def verify_item(cls, key, expected, rules=None):
        actual = cls.get_item(key)
        compare(
            expected=expected,
            actual=actual and json.loads(actual),
            rules=rules
        )
