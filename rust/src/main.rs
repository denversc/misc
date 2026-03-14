use path_clean::clean;
use std::env;
use std::io::{self, BufRead};
use std::path::{Path, PathBuf};

fn resolve(path_str: &str) -> PathBuf {
    let path = Path::new(path_str);
    let absolute_path = if path.is_absolute() {
        path.to_path_buf()
    } else {
        match env::current_dir() {
            Ok(cwd) => cwd.join(path),
            Err(_) => path.to_path_buf(), // Fallback if CWD is inaccessible
        }
    };
    clean(&absolute_path)
}

fn print_absolute_path(path_str: &str) {
    if path_str.is_empty() {
        if let Ok(cwd) = env::current_dir() {
            println!("{}", cwd.display());
        }
    } else {
        println!("{}", resolve(path_str).display());
    }
}

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();

    if !args.is_empty() {
        for arg in args {
            print_absolute_path(&arg);
        }
        return;
    }

    let stdin = io::stdin();
    let mut handle = stdin.lock();
    let mut buffer = String::new();

    loop {
        buffer.clear();
        match handle.read_line(&mut buffer) {
            Ok(0) => break, // EOF
            Ok(_) => {
                let mut line = buffer.as_str();
                if line.ends_with('\n') {
                    line = &line[..line.len() - 1];
                }
                if line.ends_with('\r') {
                    line = &line[..line.len() - 1];
                }
                print_absolute_path(line);
            }
            Err(e) => {
                if e.kind() == io::ErrorKind::InvalidData {
                    eprintln!("UTF-8 decoding error");
                } else {
                    eprintln!("Error reading stdin: {}", e);
                }
                std::process::exit(1);
            }
        }
    }
}
