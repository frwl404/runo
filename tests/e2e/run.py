import os
import subprocess
import sys

try:
    import tomllib
except ModuleNotFoundError:
    # It is bad that we import _vendor here, but there is a reason
    # for this. We don't want any external dependencies for
    # this tool (i.e. we can't use parsers, which are not available
    # in default Python installation). At the same time we want to
    # support Python versions starting from 3.9, which has no toml parser
    # officially supported (it was added only in Python 3.11).
    # So for versions older than 3.11 (while we are supporting them),
    # we will take parser from '_vendor'
    import pip._vendor.tomli as tomllib


def _test_command(command: dict):
    tests = command.get("e2e_tests", [])
    passed = set()
    failed = set()

    for test in tests:
        execute, expected_output, expected_returncode = test.split("|")
        expected_returncode = int(expected_returncode)
        res = subprocess.run(["./dev", *execute.split()], stdout=subprocess.PIPE)
        output = res.stdout.decode("utf-8")

        errors = []
        if output != expected_output:
            errors.append(f"'{expected_output}' != '{output}'")
        if res.returncode != expected_returncode:
            errors.append(f"Expected returncode: {expected_returncode}, got {res.returncode}")

        if errors:
            failed.add(execute)
            print(f"{execute} FAILED: {'; '.join(errors)}")
        else:
            print(f"{execute} PASSED")
            passed.add(execute)

    return passed, failed


def main():
    os.chdir("tests/e2e")
    config_under_the_test = "./dev.toml"
    with open(config_under_the_test, "r") as f:
        data = f.read()
        uncomment_e2e_lines = data.replace("# e2e_tests =", "e2e_tests =")

    config = tomllib.loads(uncomment_e2e_lines)

    passed = dict()
    passed_cnt = 0

    failed = dict()
    failed_cnt = 0
    for cmd in config["commands"]:
        passed[cmd["name"]], failed[cmd["name"]] = _test_command(cmd)
        passed_cnt += len(passed[cmd["name"]])
        failed_cnt += len(failed[cmd["name"]])

    print(f"SUMMARY: {passed_cnt} PASSED, {failed_cnt} FAILED")
    if failed_cnt > 0:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
