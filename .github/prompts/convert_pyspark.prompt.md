# Convert Code to pyspark

Let's convert this entire codebase from rust to pyspark with modern practices.  

Create a folder called pyspark/samlib converting the cpp code in src/samlib and rust code in rust/samlib and python code in python/samlib.

Create a .codespaces/pyspark folder with a github codespaces definition and docker file for pyspark 3.5.2 and Java.

- Include the VSCode extension for Databricks
- Include the Copilot and GitHub extensions

create a docs/pyspark_migrate folder with markdown documentation detailing the process for each file's conversion.

include github workflows to build the code using uv and ruff checks for format and style rules, pytest to run tests.

Create a readme file for building, formatting, testing and debugging on Windows and Linux using pyspark and Databricks tools.
