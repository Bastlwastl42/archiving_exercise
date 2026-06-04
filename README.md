# Archiving Exercise

This is an exercise in archiving. The given script archive-exercise.py

- has a mandatory CLI input -g/--group that must specify a user group.
- if that group is available, the scripts finds all available user of that group and their respective home folders.
- each of those home folders are aded fully to a tar archive and stored in a archive path.

## Usage

### With uv in dev

#### Requirements for development

- uv

#### Steps to run

- set up uv environment with uv sync using provided lock file
- run `uv run archive-exercise.py -g <GROUP_NAME>`

#### Steps to build

- run build.sh
- This should produce a standalone binary in archive-exercise/usr/bin
- The build script also bundles the Debian package

### Install and use using build package

```shell
sudo dpkg -i archive-exercise.deb
...

archive-exercise -g <GROUP_NAME>
```

## What the application does

Given a valid group name, all users of that group are selected and home folders identified. Using a multiprocessing
pool, for each of the identified home folders, and tar archive is created with all files of that home folder. These
archives are then stored in the configured archive path in the following structure

```shell
<GROUP_ARCHIVING_PATH>/
├─ <GROUP_NAME>/
│  ├─ <NEXT USER ID>/
│  │  ├─ <DATETIME>.tar.gz
│  ├─ <USER_ID>/
│  │  ├─ <DATETIME>.tar.gz

```

The archive Path is configured via the env variable GROUP_ARCHIVING_PATH and is defaulting to the systems temp folder,
usually `/tmp`. Continuous logfiles are created containing the same content as the output to stderr/stdout

## Notes on Testing

A dockerfile is provided that can setup a test environment where
- the build debian package is copied and installed
- a test group and test users are created for that group
- running the build docker image has a valid execution of the script as entrypoint.

```shell
# within project root
docker build -t test_archive .
# to run with predefind test entrypoint
docker run test_archive

# to run docker to explore
docker run -it test_archive
```

