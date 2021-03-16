#!/bin/sh

# Script by Persian Prince for https://github.com/OpenVisionE2
# You're not allowed to remove my copyright or reuse this script without putting this header.

setup_git() {
  git config --global user.email "bot@openvision.tech"
  git config --global user.name "Open Vision python bot"
}

commit_files() {
  git clean -fd
  rm -rf *.pyc
  rm -rf *.pyo
  rm -rf *.mo
  git checkout develop
  ./PEP8.sh
}

upload_files() {
  git remote add upstream https://${GH_TOKEN}@github.com/OpenVisionE2/enigma2-openvision-sh4.git > /dev/null 2>&1
  git push --quiet upstream develop || echo "failed to push with error $?"
}

setup_git
commit_files
upload_files
