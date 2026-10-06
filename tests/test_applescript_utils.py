import unittest

from applescript_utils import escape_applescript_string


class EscapeAppleScriptStringTests(unittest.TestCase):
    def test_escapes_backslashes(self):
        self.assertEqual(escape_applescript_string(r"C:\Users\Fab"), r"C:\\Users\\Fab")

    def test_escapes_double_quotes(self):
        self.assertEqual(escape_applescript_string('say "hello"'), 'say \\"hello\\"')

    def test_escapes_newlines(self):
        self.assertEqual(escape_applescript_string("first\nsecond"), "first\\nsecond")

    def test_escapes_carriage_returns(self):
        self.assertEqual(escape_applescript_string("first\rsecond"), "first\\rsecond")


if __name__ == "__main__":
    unittest.main()
