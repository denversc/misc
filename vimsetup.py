import logging
import os
import pathlib
import shutil
import subprocess
import urllib.request

def main():
    logging.basicConfig(level=logging.INFO)
    app = VimSetup()
    app.run()

class VimSetup:

    def run(self) -> None:
        src_dir_path = pathlib.Path.cwd()
        dest_dir_path = pathlib.Path.home()
        self.create_rc_files(src_dir_path, dest_dir_path)
        autoload_dir_path = self.create_autoload_dir(dest_dir_path)
        self.install_pathogen(autoload_dir_path)
        bundle_dir_path = self.create_bundle_dir(dest_dir_path)
        self.install_tomorrow_theme(bundle_dir_path)
        self.install_easymotion(bundle_dir_path)

    def create_rc_files(self, src_dir_path: pathlib.Path, dest_dir_path: pathlib.Path) -> None:
        for filename in (".vimrc", ".gvimrc"):
            dest_path = dest_dir_path / filename
            src_path = src_dir_path / filename
            logging.info("Creating %s", dest_path)
            with dest_path.open("wt", encoding="utf-8") as f:
                print(f"source {src_path}", file=f)

    def create_autoload_dir(self, dest_dir_path: pathlib.Path) -> pathlib.Path:
        if os.name == "nt":
            path = dest_dir_path / "vimfiles" / "autoload"
        elif os.name == "posix":
            path = dest_dir_path / ".vim" / "autoload"
        else:
            raise self.Error(f"unsupported OS: {os.name}")
        logging.info("Creating directory: %s", path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def install_pathogen(self, autoload_dir_path: pathlib.Path) -> None:
        logging.info("Installing pathogen.vim")
        pathogen_vim_path = autoload_dir_path / "pathogen.vim"
        pathogen_vim_url = "https://raw.github.com/tpope/vim-pathogen/" \
            "master/autoload/pathogen.vim"
        self.download_file(pathogen_vim_url, pathogen_vim_path)

    def download_file(self, url: str, dest_path: pathlib.Path) -> None:
        logging.info("Downloading %s to %s", url, dest_path)
        infile = urllib.request.urlopen(url)
        try:
            with dest_path.open("wb") as outfile:
                while True:
                    buf = infile.read(2048)
                    if len(buf) == 0:
                        break
                    outfile.write(buf)
        finally:
            infile.close()

    def create_bundle_dir(self, dest_dir_path: pathlib.Path) -> pathlib.Path:
        if os.name == "nt":
            path = dest_dir_path / "vimfiles" / "bundle"
        elif os.name == "posix":
            path = dest_dir_path / ".vim" / "bundle"
        else:
            raise self.Error(f"unsupported OS: {os.name}")
        logging.info("Creating directory: %s", path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def install_tomorrow_theme(self, bundle_dir_path: pathlib.Path) -> None:
        logging.info("Installing Tomorrow Night color scheme")
        install_dir_path = bundle_dir_path / "vim-tomorrow-theme" / "colors"
        logging.info("Creating directory: %s", install_dir_path)
        install_dir_path.mkdir(parents=True, exist_ok=True)
        vim_url = "https://raw.github.com/chriskempson/tomorrow-theme/" \
            "master/vim/colors/Tomorrow-Night-Bright.vim"
        vim_path = install_dir_path / "Tomorrow-Night-Bright.vim"
        self.download_file(vim_url, vim_path)

    def install_easymotion(self, bundle_dir_path: pathlib.Path) -> None:
        git_repo_url = "https://github.com/Lokaltog/vim-easymotion.git"
        install_dir_path = bundle_dir_path / "easymotion"
        if install_dir_path.is_dir():
            logging.info("Deleting directory: %s", install_dir_path)
            shutil.rmtree(install_dir_path)
        self.git_clone(git_repo_url, install_dir_path)

    def git_clone(self, repo_url: str, dest_dir_path: pathlib.Path) -> None:
        logging.info("Cloning Git repository %s into %s", repo_url, dest_dir_path)
        args = ["git", "clone", repo_url, str(dest_dir_path)]
        logging.info("Running command: %s", subprocess.list2cmdline(args))
        subprocess.check_call(args)


if __name__ == "__main__":
    main()
