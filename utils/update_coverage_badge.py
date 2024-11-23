coverage_patch = ""

with open("code-coverage-results.md", "r") as coverage:
    coverage_patch = coverage.readline()

if coverage_patch == "":
    exit(0)

with open("README.md", "r+") as readme:
    lines = readme.readlines()

    written = False

    for i, line in enumerate(lines):
        if "![Code Coverage]" in line:
            lines[i] = coverage_patch
            written = True

    if not written:
        lines = [coverage_patch] + lines

    readme.seek(0)
    readme.writelines(lines)
    readme.truncate()