
# Just returns 0 (which linux 'thinks' of as: "Everything is OK" or "No Errors")

# test_for_builds.py
def run_all_tests():
    return 0


if __name__ == "__main__":
    retValue = run_all_tests()
    exit(retValue)