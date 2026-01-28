#!/bin/bash
# 自动部署脚本：用法 ./deploy.sh <项目名> <GitHub_Token>

PROJECT_NAME=$1
GH_TOKEN=$2
OPENCODE_A2A_DIR="${OPENCODE_A2A_DIR:-/opt/opencode-a2a/opencode-a2a-serve}"

if [ -z "$PROJECT_NAME" ] || [ -z "$GH_TOKEN" ]; then
    echo "用法: $0 <项目名> <该项目专属的FGT_Token>"
    exit 1
fi

echo "--- 正在部署项目: $PROJECT_NAME ---"

# 1. 创建子用户（如果不存在）
if ! id "$PROJECT_NAME" &>/dev/null; then
    sudo adduser --system --group --home /data/projects/$PROJECT_NAME $PROJECT_NAME
fi

# 2. 建立工作目录
sudo mkdir -p /data/projects/$PROJECT_NAME/workspace
sudo chown -R $PROJECT_NAME:$PROJECT_NAME /data/projects/$PROJECT_NAME

# 3. 生成该实例专用的 Systemd 配置文件
# 我们动态生成配置文件，把 Token 塞进去
SERVICE_FILE="/etc/systemd/system/opencode-a2a@$PROJECT_NAME.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=OpenCode A2A for $PROJECT_NAME
After=network.target

[Service]
User=$PROJECT_NAME
Group=$PROJECT_NAME
WorkingDirectory=/data/projects/$PROJECT_NAME
# 注入专属 Token 供 gh 和 git 使用
Environment=GH_TOKEN=$GH_TOKEN
Environment=HOME=/data/projects/$PROJECT_NAME
# 强制 Git 身份
Environment=GIT_AUTHOR_NAME="OpenCode-$PROJECT_NAME"
Environment=GIT_COMMITTER_NAME="OpenCode-$PROJECT_NAME"
Environment=GIT_AUTHOR_EMAIL="$PROJECT_NAME@internal"
Environment=GIT_COMMITTER_EMAIL="$PROJECT_NAME@internal"

# 执行命令
ExecStart=$OPENCODE_A2A_DIR/.venv/bin/python $OPENCODE_A2A_DIR/main.py \
    --workspace /data/projects/$PROJECT_NAME/workspace

# 隔离权限
ProtectSystem=strict
ReadWritePaths=/data/projects/$PROJECT_NAME
ReadOnlyPaths=$OPENCODE_A2A_DIR
ReadOnlyPaths=/opt/.opencode

[Install]
WantedBy=multi-user.target
EOF

# 4. 启动服务
sudo systemctl daemon-reload
sudo systemctl enable --now opencode-a2a@$PROJECT_NAME

echo "--- 部署完成！ ---"
sudo systemctl status opencode-a2a@$PROJECT_NAME --no-pager
