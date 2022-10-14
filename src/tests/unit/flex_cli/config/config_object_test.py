import json
import unittest

from flex_cli.config import merge
from flex_cli.config.exception import InvalidConfigurationMergeParams


class VerifyMergeDictTest(unittest.TestCase):

    def test_merge_dict_ok(self):
        tests = {
            "one_level_overwrite": [
                {"test": 'test'},
                {"test": 'overwrite'},
                {"test": 'overwrite'}
            ],
            "one_level_overwrite_reverse": [
                {"test": 'dont_overwrite'},
                {"test": 'test'},
                {"test": 'test'}
            ],
            "2_levels_overwrite": [
                {"test": {'test': 'test'}},
                {"test": {'test': 'overwrite'}},
                {"test": {'test': 'overwrite'}},
            ],
            "2_levels_overwrite_reverse": [
                {"test": {'test': 'dont_overwrite'}},
                {"test": {'test': 'test'}},
                {"test": {'test': 'test'}},
            ],
            "first_dict_empty": [
                {},
                {"test": 'test'},
                {"test": 'test'}
            ],
            "second_dict_empty": [
                {"test": 'test'},
                {},
                {"test": 'test'}
            ]
        }
        for test_name, test in tests.items():
            dict1 = test[0]
            dict2 = test[1]
            expected_result = test[2]
            self.assert_merge_dict(dict1, dict2, expected_result, test_name)

    def test_merge_dict_with_list_ok(self):
        tests = {
            "one_level_merge_list": [
                {"test": ['test1']},
                {"test": ['test2']},
                {"test": ['test1', 'test2']}
            ]
        }
        for test_name, test in tests.items():
            dict1 = test[0]
            dict2 = test[1]
            expected_result = test[2]
            self.assert_merge_dict(dict1, dict2, expected_result, test_name)

    def test_merge_dict_with_list_failing(self):
        tests = {
            "one_level_merge_list_second_param": [
                {"test": ['test1']},
                {"test": ["test2", {"test": "test"}]}
            ],
            "one_level_merge_list_first_param": [
                {"test": ['test1', {"test": "test"}]},
                {"test": ["test2"]}
            ],
            "one_level_merge_list_second_param_empty": [
                {"test": [{"test": "test"}]},
                {"test": []},
            ]
        }
        for test_name, test in tests.items():
            dict1 = test[0]
            dict2 = test[1]
            with self.assertRaises(InvalidConfigurationMergeParams) as context:
                merge.dict_merge(dict1, dict2)
            self.assertTrue(InvalidConfigurationMergeParams.error_code == context.exception.error_code)

    def assert_merge_dict(self, dict1: dict, dict2: dict, expected_result: dict, message: str):
        """
        Merge dictionary assertion mainly used for success cases
        """
        result = merge.dict_merge(dict1, dict2)
        self.assertTrue(result == expected_result, "Failed test " + message + json.dumps(expected_result))


if __name__ == "__main__":
    unittest.main()
