# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import io
import os
import subprocess
import sys
import urllib2

###############################################################################

def main():
    app = VimSetup()
    app.run()
    return 0

###############################################################################

class VimSetup(object):

    def __init__(self, log_func=print):
        self.log_func = log_func

    def run(self):
        src_dir_path = os.path.abspath(".")
        dest_dir_path = os.path.expanduser("~")
        self.create_rc_files(src_dir_path, dest_dir_path)
        autoload_dir_path = self.create_autoload_dir(dest_dir_path)
        self.install_pathogen(autoload_dir_path)
        bundle_dir_path = self.create_bundle_dir(dest_dir_path)
        self.install_tomorrow_theme(bundle_dir_path)
        self.install_easymotion(bundle_dir_path)

    def create_rc_files(self, src_dir_path, dest_dir_path):
        for filename in (".vimrc", ".gvimrc"):
            dest_path = os.path.join(dest_dir_path, filename)
            src_path = os.path.join(src_dir_path, filename)
            self.log("Creating {}".format(dest_path))
            with io.open(dest_path, "wt", encoding="utf-8") as f:
                print("source {}".format(src_path), file=f)

    def create_autoload_dir(self, dest_dir_path):
        if os.name == "nt":
            path = os.path.join(dest_dir_path, "vimfiles", "autoload")
        elif os.name == "posix":
            path = os.path.join(dest_dir_path, ".vim", "autoload")
        else:
            raise self.Error("unsupported OS: {}".format(os.name))
        self.mkdir(path)
        return path

    def install_pathogen(self, autoload_dir_path):
        self.log("Installing pathogen.vim")
        pathogen_vim_path = os.path.join(autoload_dir_path, "pathogen.vim")
        pathogen_vim_url = "https://raw.github.com/tpope/vim-pathogen/" \
            "master/autoload/pathogen.vim"
        self.download_file(pathogen_vim_url, pathogen_vim_path)

    def download_file(self, url, dest_path):
        self.log("Downloading {} to {}".format(url, dest_path))
        infile = urllib2.urlopen(url)
        try:
            with io.open(dest_path, "wb") as outfile:
                while True:
                    buf = infile.read(2048)
                    if len(buf) == 0:
                        break
                    outfile.write(buf)
        finally:
            infile.close()

    def create_bundle_dir(self, dest_dir_path):
        if os.name == "nt":
            path = os.path.join(dest_dir_path, "vimfiles", "bundle")
        elif os.name == "posix":
            path = os.path.join(dest_dir_path, ".vim", "bundle")
        else:
            raise self.Error("unsupported OS: {}".format(os.name))
        self.mkdir(path)
        return path

    def install_tomorrow_theme(self, bundle_dir_path):
        self.log("Installing Tomorrow Night color scheme")
        install_dir_path = os.path.join(bundle_dir_path, "vim-tomorrow-theme",
            "colors")
        self.mkdir(install_dir_path)
        vim_url = "https://raw.github.com/chriskempson/tomorrow-theme/" \
            "master/vim/colors/Tomorrow-Night-Bright.vim"
        vim_path = os.path.join(install_dir_path, "Tomorrow-Night-Bright.vim")
        self.download_file(vim_url, vim_path)

    def install_easymotion(self, bundle_dir_path):
        git_repo_url = "https://github.com/Lokaltog/vim-easymotion.git"
        install_dir_path = os.path.join(bundle_dir_path, "easymotion")
        self.git_clone(git_repo_url, install_dir_path)

    def mkdir(self, path):
        self.log("Creating directory: {}".format(path))
        if not os.path.isdir(path):
            os.makedirs(path)

    def git_clone(self, repo_url, dest_dir_path):
        self.log("Cloning Git repository {} into {}"
            .format(repo_url, dest_dir_path))
        args = ["git", "clone", repo_url, dest_dir_path]
        args_str = subprocess.list2cmdline(args)
        self.log(args_str)
        process = subprocess.Popen(args)
        process.wait()
        if process.returncode != 0:
            raise Exception("command completed with non-zero exit code {}: {}"
                .format(process.returncode, args_str))

    def log(self, message):
        log_func = self.log_func
        if log_func is not None:
            log_func(message)

###############################################################################

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
