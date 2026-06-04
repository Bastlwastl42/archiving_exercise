# This is a test target container file.
FROM debian

WORKDIR /usr/src

COPY archive-exercise.deb .

RUN dpkg -i archive-exercise.deb

RUN groupadd test_archive_group

RUN useradd --create-home -g test_archive_group test_user_one
RUN useradd --create-home -g test_archive_group test_user_two
RUN useradd --create-home -g test_archive_group test_user_four

CMD archive-exercise -g test_archive_group