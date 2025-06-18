import re
import unicodedata
from textwrap import dedent

class FilterInputUtility:
    """Simple utility to normalize the input that is given by the user, while talking to the Agent"""

    @staticmethod
    def filter_input(input: str) -> str:
        input = dedent(input).strip()
        input = unicodedata.normalize("NFKC", input)
        input = re.sub(r'\n{2,}', '\n', input)
        input = re.sub(r'[ \t]{2,}', ' ', input)
        input = input.replace('“', '"').replace('”', '"').replace("‘", "'").replace("’", "'")
        input = re.sub(r'\s+([.,!?;:])', r'\1', input)
        input = re.sub(r'([.,!?;:])(?=\S)', r'\1', input)

        return input

input_filter = FilterInputUtility()