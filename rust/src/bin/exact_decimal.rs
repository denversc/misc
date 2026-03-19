use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    if let Err(e) = io::stdin().read_to_string(&mut input) {
        eprintln!("Failed to read standard input: {}", e);
        std::process::exit(1);
    }

    let input = input.trim();
    if input.is_empty() {
        return;
    }

    let d: f64 = match input.parse() {
        Ok(v) => v,
        Err(_) => {
            // Try matching Java's Infinity/NaN strings if Rust's f64::from_str doesn't natively parse it
            if input == "Infinity" || input == "+Infinity" {
                std::f64::INFINITY
            } else if input == "-Infinity" {
                std::f64::NEG_INFINITY
            } else if input == "NaN" {
                std::f64::NAN
            } else {
                eprintln!("Failed to parse input as double: {}", input);
                std::process::exit(1);
            }
        }
    };

    if d.is_nan() || d.is_infinite() {
        eprintln!("BigDecimal does not accept NaN or Infinity");
        std::process::exit(1);
    }

    let s = format!("{:.1074}", d);
    let mut trimmed = s.trim_end_matches('0').to_string();
    if trimmed.ends_with('.') {
        trimmed.pop();
    }
    if trimmed == "-0" {
        trimmed = "0".to_string();
    }

    println!("{}", trimmed);
}
