install_path=$1
user=$(whoami)
group=$(id -gn)

python3 -m venv "$install_path/venv"
"$install_path/venv/bin/pip3" install flask gunicorn

sudo tee /etc/systemd/system/assets.service > /dev/null << EOF
[Unit]
Description=Assets distribution server
After=network.target

[Service]
User=$user
Group=$group
WorkingDirectory=$install_path
Environment=PATH=$install_path/venv/bin:/usr/local/bin:/usr/bin:/bin
Environment=DATABASE_PATH=$install_path/assets.db
Environment=INDEX_PATH=$install_path/index.html
ExecStart=$install_path/venv/bin/gunicorn app:app -b 127.0.0.1:7000
MemoryMax=1G
CPUQuota=50%
Restart=always

[Install]
WantedBy=multi-user.target

EOF

sudo systemctl enable --now assets.service
