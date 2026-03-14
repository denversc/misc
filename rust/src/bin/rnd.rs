use clap::{Arg, ArgAction, Command};
use rand::{Rng, thread_rng};
use rand::distributions::Alphanumeric;
use arboard::Clipboard;

fn main() {
    let matches = Command::new("rnd")
        .override_usage("rnd [options]")
        .help_template("usage: {usage}\n\noptions:\n{options}")
        .disable_help_flag(true)
        .arg(
            Arg::new("help")
                .short('h')
                .long("help")
                .help("show this help message and exit")
                .action(ArgAction::Help)
        )
        .arg(
            Arg::new("count")
                .short('n')
                .long("count")
                .value_name("COUNT")
                .help("The number of random values to generate (default: 1)")
                .default_value("1")
                .value_parser(clap::value_parser!(usize))
        )
        .arg(
            Arg::new("length")
                .short('l')
                .long("length")
                .value_name("LENGTH")
                .help("The number of characters in the random string (default: 10)")
                .default_value("10")
                .value_parser(clap::value_parser!(usize))
        )
        .arg(
            Arg::new("first_char_alpha")
                .long("first-char-alpha")
                .help("Ensure that the first character of the generated string is a letter, as opposed to a number. (default: True)")
                .action(ArgAction::SetTrue)
        )
        .arg(
            Arg::new("no_first_char_alpha")
                .long("no-first-char-alpha")
                .help("Removes the requirement that the first character of the generated string will be a letter, making it possible for the first character to be either\na letter or a number. This is the opposite of --first-char-alpha.")
                .action(ArgAction::SetTrue)
                .conflicts_with("first_char_alpha")
        )
        .arg(
            Arg::new("string")
                .long("string")
                .help("Generate a string (this is the default)")
                .action(ArgAction::SetTrue)
        )
        .arg(
            Arg::new("uint32")
                .long("uint32")
                .visible_alias("u32")
                .help("Generate a 32-bit unsigned integer")
                .action(ArgAction::SetTrue)
        )
        .arg(
            Arg::new("int32")
                .long("int32")
                .visible_alias("i32")
                .help("Generate a 32-bit signed integer")
                .action(ArgAction::SetTrue)
        )
        .arg(
            Arg::new("uint64")
                .long("uint64")
                .visible_alias("u64")
                .help("Generate a 64-bit unsigned integer")
                .action(ArgAction::SetTrue)
        )
        .arg(
            Arg::new("int64")
                .long("int64")
                .visible_alias("i64")
                .help("Generate a 32-bit signed integer")
                .action(ArgAction::SetTrue)
        )
        .arg(
            Arg::new("copy_to_clipboard")
                .short('c')
                .long("copy-to-clipboard")
                .help("Copy the generated text to the clipboard (this is the default behavior)")
                .action(ArgAction::SetTrue)
        )
        .arg(
            Arg::new("no_copy_to_clipboard")
                .short('C')
                .long("no-copy-to-clipboard")
                .help("Do NOT copy the generated text to the clipboard; negates the effects of -c/--copy-to-clipboard")
                .action(ArgAction::SetTrue)
                .conflicts_with("copy_to_clipboard")
        )
        .get_matches();

    let count = *matches.get_one::<usize>("count").unwrap();
    let length = *matches.get_one::<usize>("length").unwrap();

    let no_first_char_alpha = matches.get_flag("no_first_char_alpha");
    let first_char_alpha = !no_first_char_alpha;

    let uint32 = matches.get_flag("uint32");
    let int32 = matches.get_flag("int32");
    let uint64 = matches.get_flag("uint64");
    let int64 = matches.get_flag("int64");

    let no_copy = matches.get_flag("no_copy_to_clipboard");
    let copy = !no_copy;

    let mut rng = thread_rng();
    let mut results = Vec::new();

    for _ in 0..count {
        if uint32 {
            results.push(rng.gen::<u32>().to_string());
        } else if int32 {
            results.push(rng.gen::<i32>().to_string());
        } else if uint64 {
            results.push(rng.gen::<u64>().to_string());
        } else if int64 {
            results.push(rng.gen::<i64>().to_string());
        } else {
            if length == 0 {
                results.push(String::new());
                continue;
            }

            let mut s = String::with_capacity(length);
            
            let first_char = if first_char_alpha {
                loop {
                    let c: char = rng.sample(Alphanumeric).into();
                    if c.is_ascii_alphabetic() {
                        break c;
                    }
                }
            } else {
                rng.sample(Alphanumeric).into()
            };
            s.push(first_char);

            for _ in 1..length {
                s.push(rng.sample(Alphanumeric).into());
            }
            results.push(s);
        }
    }

    let output = results.join("\n");
    if count > 0 {
        println!("{}", output);
    }

    if copy && count > 0 {
        if let Ok(mut clipboard) = Clipboard::new() {
            let _ = clipboard.set_text(output);
        }
    }
}
