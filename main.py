import argparse
import grp
import multiprocessing
import pwd
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path

from loguru import logger

ARCHIVE_PATH = Path(tempfile.gettempdir())
PROCESSES = 4

logger.add('archive_exercise.log')


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


def archive_path(to_be_archived: Path, archive_target: Path) -> list[tarfile.TarInfo]:
    """
    Archive a given path as tar.gz to target Path. If the provided target is not a dir, a suitable archive file name is set.
    This would also be a good place to include some kind of filtering if not archiving certain files is desired.
    :param to_be_archived:
    :param archive_target:
    :return:
    """
    archive_target = archive_target.resolve()
    if not archive_target.parent.exists():
        archive_target.parent.mkdir(parents=True)
    if archive_target.is_dir():
        archive_target = Path(
            archive_target, f'{datetime.now().strftime("%Y%m%d_%H-%M-%S-%f")}.tar.gz'
        )

    with tarfile.open(archive_target, 'x:gz') as tar_archive:
        tar_archive.add(to_be_archived)
        cur_tar_members = tar_archive.getmembers()
    logger.info(
        f'Finished archiving {to_be_archived} to target {archive_target}. '
        f'Archive has {len(cur_tar_members)} members'
    )
    return cur_tar_members


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
        print('Group does not exist.')
        logger.critical(f'The provided group name {group_name} is not found.')
        exit(1)
    logger.info(f'Found Group with Name {group_name}, group ID is {archive_group_struct.gr_gid}')
    user_list = get_user_per_group_id(archive_group_struct)
    logger.info(f'Identified {len(user_list)} user in group {archive_group_struct.gr_gid}.')
    archive_home_folder_per_user(user_list, group_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='ArchiveExercise',
        description='This is an exercise in archiving. '
        'This script should archive home folders of all users in a given user group list.',
        epilog='Text at the bottom of help',
    )

    parser.add_argument(
        '--group',
        '-g',
        help='Specify the group name to archive those groups members. Mandatory.',
    )
    args = parser.parse_args()

    main(args.group)
