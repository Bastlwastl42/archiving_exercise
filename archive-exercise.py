import argparse
import grp
import multiprocessing
import os
import pwd
import sys
import tempfile
from pathlib import Path

from loguru import logger

from archive_path import archive_path

ARCHIVE_PATH = os.environ.get('GROUP_ARCHIVING_PATH', Path(tempfile.gettempdir()))
PROCESSES = 4

logger.add('archive_exercise.log')
multiprocessing.freeze_support()


def get_user_per_group_id(group: grp.struct_group) -> list[tuple[int, Path]]:
    """
    For a given group struct, return the list of users home folders and ids
    :param group: input group name as group struct, members are in attribute gr_mem NOT use direct gid filtering instead
    :return: A list of tuples with user ID and home folder as path
    """
    ret_list: list[tuple[int, Path]] = []
    for user in [u for u in pwd.getpwall() if u.pw_gid == group.gr_gid]:
        ret_list.append((user.pw_uid, Path(user.pw_dir)))
    return ret_list


def archive_home_folder_per_user(user_list: list[tuple[int, Path]], group_name: str):
    """
    Walk over given uer list and archive home folder as tar file.
    :param user_list:
    :param group_name
    :return:
    """
    logger.debug(f'starting archiving to {ARCHIVE_PATH}.')
    archive_task_list: list = []
    for user_id, home_folder in user_list:
        new_archive_path = Path(ARCHIVE_PATH, group_name, user_id.__str__())
        if not new_archive_path.exists():
            new_archive_path.mkdir(parents=True)
        archive_task_list.append((home_folder, new_archive_path))

    with multiprocessing.Pool(PROCESSES) as pool:
        archiving_results = pool.starmap_async(archive_path, archive_task_list)
        archiving_results.wait()
    logger.debug('finished archiving')


def main(group_name: str):
    """
    Main loop and setup
    :param group_name: group name to archive
    :return:
    """
    try:
        archive_group_struct = grp.getgrnam(group_name)
    except KeyError:
        logger.critical(f'The provided group name {group_name} is not found.')
        sys.exit(1)
    logger.info(f'Found Group with Name {group_name}, group ID is {archive_group_struct.gr_gid}')
    user_list = get_user_per_group_id(archive_group_struct)
    logger.info(f'Identified {len(user_list)} user in group {archive_group_struct.gr_gid}.')
    archive_home_folder_per_user(user_list, group_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='ArchiveExercise',
        description='This is an exercise in archiving. '
        'This script should archive home folders of all users in a given user group list.',
        epilog='This is an Exercise. There is even less then absolutely NO WARRANTY.',
    )

    parser.add_argument(
        '--group',
        '-g',
        help='Specify the group name to archive those groups members. Mandatory.',
        required=True,
    )
    args = parser.parse_args()

    main(args.group)
