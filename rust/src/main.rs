use arboard::Clipboard;
use clap::{Arg, ArgAction, Command};
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

fn get_absolute_path(path_str: &str) -> String {
    if path_str.is_empty() {
        if let Ok(cwd) = env::current_dir() {
            cwd.display().to_string()
        } else {
            String::new()
        }
    } else {
        resolve(path_str).display().to_string()
    }
}

fn main() {
    let matches = Command::new("abspath")
        .about("Prints the absolute path of the given files")
        .arg(
            Arg::new("paths")
                .help("The paths to resolve. If zero paths are given, reads from standard input.")
                .num_args(0..)
                .action(ArgAction::Append),
        )
        .arg(
            Arg::new("copy_to_clipboard")
                .short('c')
                .long("copy-to-clipboard")
                .help("Copy the generated text to the clipboard (this is the default behavior)")
                .action(ArgAction::SetTrue),
        )
        .arg(
            Arg::new("no_copy_to_clipboard")
                .short('C')
                .long("no-copy-to-clipboard")
                .help("Do NOT copy the generated text to the clipboard; negates the effects of -c/--copy-to-clipboard")
                .action(ArgAction::SetTrue)
                .conflicts_with("copy_to_clipboard"),
        )
        .get_matches();

    let paths: Vec<String> = matches
        .get_many::<String>("paths")
        .map(|v| v.cloned().collect())
        .unwrap_or_default();

    let no_copy = matches.get_flag("no_copy_to_clipboard");
    let copy = !no_copy;

    let mut results = Vec::new();

    if !paths.is_empty() {
        for path in paths {
            let abs_path = get_absolute_path(&path);
            println!("{}", abs_path);
            results.push(abs_path);
        }
    } else {
        let stdin = io::stdin();
        let mut handle = stdin.lock();
        let mut buffer = String::new();

        loop {
            buffer.clear();
            match handle.read_line(&mut buffer) {
                Ok(0) => break, // EOF
                Ok(_) => {
                    let line = buffer.trim_end();
                    let abs_path = get_absolute_path(line);
                    println!("{}", abs_path);
                    results.push(abs_path);
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

    if copy && !results.is_empty() {
        let output = results.join("\n");
        if let Ok(mut clipboard) = Clipboard::new() {
            let _ = clipboard.set_text(output).unwrap_or(());
        }
    }
}
