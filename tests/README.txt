Run the tests using Python's built-in unittest framework:
    python -m unittest discover -s tests

This command will automatically discover and run all the test files in the tests/ directory.

********************************************************************************************

pytest is a more powerful testing tool and easier to use compared to unittest.

1. Install pytest
    pip install pytest

2. Run the tests with pytest:
    pytest

If you're running the tests from the project root, pytest will automatically discover the test files (which usually start with test_).

********************************************************************************************

Run with coverage report (if you want to track how much code is covered by the tests):

    pip install pytest-cov
    pytest --cov=app tests/

This will display a code coverage report in the terminal and highlight any untested parts of the app