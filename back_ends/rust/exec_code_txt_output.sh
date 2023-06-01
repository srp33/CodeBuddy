echo "[package]" > Cargo.toml
echo "name = \"test-project\"" >> Cargo.toml
echo "version = \"0.1.0\"" >> Cargo.toml
echo "authors = [\"ChatGPT\"]" >> Cargo.toml
echo "edition = \"2021\"" >> Cargo.toml
echo  >> Cargo.toml
echo "[dependencies]" >> Cargo.toml

mkdir -p src
cat before_code main_code after_code > src/main.rs

cargo run