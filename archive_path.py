import tarfile
from datetime import datetime
from pathlib import Path

from loguru import logger


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
