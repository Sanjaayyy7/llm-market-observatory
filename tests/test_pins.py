import importlib.metadata as md
import sys

import duckdb
from lifelines import KaplanMeierFitter


def test_pins():
    assert sys.version_info[:2] == (3, 12)
    major, minor = (int(x) for x in duckdb.__version__.split(".")[:2])
    assert major == 1 and minor >= 5
    assert md.version("dbt-core").startswith("1.12.")
    assert md.version("pandas").startswith("2.")
    kmf = KaplanMeierFitter().fit([1, 2, 3], [1, 0, 1])
    assert len(kmf.survival_function_) == 4
