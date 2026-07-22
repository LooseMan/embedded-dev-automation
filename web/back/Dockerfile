# pythonの公式イメージはdebian系である
# 本リポジトリはredhat系をベースにしたいため、
# almalinuxに必要なパッケージを追加する
FROM almalinux:9

# 以下の理由からOS更新は実施しない
# 1. イメージのサイズが肥大化する
# 2. ビルドが遅くなり、壊れる原因になる
# 3. 公式イメージはすでに定期更新されている
# RUN dnf -y update

# パッケージインストール（ドキュメント・キャッシュを除外）
# alma9標準のpythonはv3.9で古いため、別途v3.12（alma10の標準）をインストールする
RUN dnf -y install --nodocs \
        python3.12 \
        python3.12-pip && \
    dnf clean all && \
    rm -rf /var/cache/dnf

# 作業ディレクトリ
WORKDIR /workspace

# 依存関係のインストール（ビルドの高速化のため、コードより先にインストール）
COPY requirements.txt .
RUN pip3.12 install --no-cache-dir -r requirements.txt

# アプリケーションコード（appフォルダ）のみをコンテナ内にコピー
COPY app ./app

# コンテナ起動時に FastAPI サーバーを自動起動
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
