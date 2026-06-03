import os
import argparse

def check_group_list():
    return os.getgroups()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='ArchiveExercise',
        description='This is an exercise in archiving. This script should archive home folders of all users in a given user group list.',
        epilog='Text at the bottom of help')

