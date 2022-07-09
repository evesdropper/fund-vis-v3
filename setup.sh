mkdir -p ~/.streamlit/

echo "[theme]
base = 'light'
[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
