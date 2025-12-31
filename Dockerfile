# Pythonの軽量イメージを使用
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# 依存ファイルをコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ソースコードをコピー
COPY . .

# Streamlitが使用するポートを環境変数として設定（Cloud RunはPORT環境変数を自動注入する）
# デフォルトは8080にしておく
ENV PORT=8080

# コンテナ起動時に実行するコマンド
# server.portに$PORTを指定して起動
CMD streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0