# pytestをFastAPI開発環境へ導入する

この資料では、FastAPIアプリケーションに対するUnit Test環境としてpytestを導入し、REST APIを自動テストできる環境を構築するために実施した対応を整理します。

---

# はじめに

本プロジェクトでは、FastAPIを用いてREST APIを実装しています。

APIの品質を維持しながら継続的に開発を行うため、FastAPIアプリケーションを起動することなくAPIを実行できるUnit Test環境としてpytestを導入します。

本手順は実際の導入・動作確認結果をもとに作成しており、導入時に発生した問題とその対処方法も合わせて記載します。

---

# やりたいこと

pytestをFastAPIプロジェクトへ導入し、REST APIのUnit Testを実行できるようにします。

最終的に以下を実現します。

* FastAPIを起動せずREST APIをテストできる
* API変更時に回帰試験を実行できる
* CI環境でも同一のテストを実行できる

---

# 検証環境

本手順は以下の環境で動作確認しています。

| 項目             | 内容            |
| -------------- | ------------- |
| OS             | macOS Sequoia |
| Python         | 3.12.3        |
| FastAPI        | 0.139.2       |
| httpx          | 0.28.x        |
| pytest         | 9.1.1         |
| pytest-asyncio | 1.4.0         |
| ネットワーク         | オンライン         |
| 仮想環境           | venv          |
| パッケージ管理        | pip           |

> **注意**
>
> Pythonのバージョンよりもライブラリのバージョン差異による影響が大きいため、異なるバージョンを利用する場合は公式ドキュメントも併せて確認してください。

---

# 前提条件

* Python 3.12系が利用できること
* Python仮想環境(venv)を利用していること
* FastAPIアプリケーションが動作すること
* インターネットへ接続できること

---

# 必要な対応

| 対応            | 場所     | 目的                      |
| ------------- | ------ | ----------------------- |
| 対応.1 pytest導入 | 開発環境   | Unit Testライブラリを導入する     |
| 対応.2 pytest設定 | プロジェクト | pytest実行環境を設定する         |
| 対応.3 テスト作成    | プロジェクト | REST APIのUnit Testを作成する |
| 対応.4 動作確認     | 開発環境   | pytestが正常に動作することを確認する   |

---

# 対応.1 pytest導入

FastAPIの非同期APIをテストするため、pytestおよび関連ライブラリを導入します。

## 手順

```sh
pip install pytest pytest-asyncio httpx
```

requirements.txtを更新します。

```sh
pip freeze > requirements.txt
```

## 確認

```sh
pytest --version
```

期待する状態

* pytestのバージョンが表示される
* エラーなく終了する

---

# 対応.2 pytest設定

pytest実行時にFastAPIプロジェクトを参照できるよう設定します。

プロジェクトルートへ

```text
pytest.ini
```

を作成します。

## 手順

```ini
[pytest]
testpaths = tests
pythonpath = .
asyncio_mode = auto
```

## 確認

テスト一覧を取得します。

```sh
python -m pytest --collect-only
```

期待する状態

* testsディレクトリが認識される
* テスト一覧が表示される

---

### Trouble.1 ModuleNotFoundError: No module named 'app'

#### 症状

```text
ModuleNotFoundError: No module named 'app'
```

#### 原因

pytest実行時にプロジェクトルートがPythonのモジュール検索パスへ追加されていませんでした。

#### 対応

pytest.iniへ

```ini
pythonpath = .
```

を追加します。

確認

```sh
python -c "from app.main import app"
```

期待する状態

* エラーが発生しない

---

# 対応.3 テスト作成

以下の構成でテストを配置します。

```text
back/
├── app/
├── tests/
│   ├── conftest.py
│   └── test_unit_status.py
└── pytest.ini
```

---

## conftest.py

FastAPI最新版ではhttpx 0.28以降の仕様に合わせ、ASGITransportを利用します。

```python
import pytest_asyncio

from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest_asyncio.fixture
async def client():

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client
```

---

## test_unit_status.py

POST APIのUnit Test例です。

```python
import pytest


@pytest.mark.asyncio
async def test_post_unit_status(client):

    response = await client.post(
        "/unit_status",
        json={
            "unit_id": 1,
            "status": "RUNNING"
        },
    )

    assert response.status_code == 200
```

---

### Trouble.2 requested an async fixture 'client'

#### 症状

```text
requested an async fixture 'client'
```

#### 原因

pytest-asyncio 1.xでは非同期Fixtureの定義方法が変更されています。

#### 対応

以下ではなく

```python
@pytest.fixture
```

以下を利用します。

```python
@pytest_asyncio.fixture
```

---

### Trouble.3 AsyncClient() got an unexpected keyword argument 'app'

#### 症状

```text
TypeError:
AsyncClient.__init__() got an unexpected keyword argument 'app'
```

#### 原因

httpx 0.28以降では

```python
AsyncClient(app=app)
```

が廃止されています。

#### 対応

ASGITransportを利用します。

```python
transport = ASGITransport(app=app)

AsyncClient(
    transport=transport,
    base_url="http://test",
)
```

---

### Trouble.4 HTTP 404 Not Found

#### 症状

テストは実行されるがHTTPステータスコード404が返る。

#### 原因

テスト対象URLがFastAPIへ登録されていません。

#### 確認

登録済みエンドポイントを確認します。

```sh
python -c "from app.main import app; print([(r.path, list(r.methods)) for r in app.routes])"
```

#### 対応

実装済みAPIに合わせてテストコードを修正します。

---

# 対応.4 動作確認

## 手順

```sh
python -m pytest
```

## 確認

期待する状態

* テストがPASSする
* HTTPステータスコードが期待値と一致する
* エラーが発生しない

実行例

```text
========================
2 passed
========================
```

---

# 設定値の意味

| 項目            | 例       | 説明                           |
| ------------- | ------- | ---------------------------- |
| testpaths     | tests   | テスト対象ディレクトリ                  |
| pythonpath    | .       | プロジェクトルートをモジュール検索パスへ追加       |
| asyncio_mode  | auto    | pytest-asyncioの実行モード         |
| ASGITransport | app=app | FastAPIアプリケーションへ直接リクエストを送信する |

---

# トラブルシューティング

### pytestコマンドで期待したPythonが利用されない

確認すること

```sh
which python
which pytest
```

仮想環境配下を利用していることを確認します。

```text
.venv/bin/python
.venv/bin/pytest
```

---

### ModuleNotFoundError

確認すること

```sh
python -c "from app.main import app"
```

原因

* pytest.ini未設定
* pythonpath未設定

---

### AsyncClientエラー

原因

* httpx 0.28以降の仕様変更

解決方法

* ASGITransportを利用する

---

### 非同期Fixtureエラー

原因

* pytest.fixtureを利用している

解決方法

* pytest_asyncio.fixtureへ変更する

---

# おわりに（教訓）

pytestを導入することで、FastAPIを起動することなくREST APIを実行できるUnit Test環境を構築できました。

今回の導入では、Python本体よりもライブラリのバージョン差異による影響が大きく、特に以下の点が重要でした。

* pytest.iniを作成し、モジュール検索パスを設定する
* pytest-asyncioでは`pytest_asyncio.fixture`を利用する
* httpx 0.28以降では`ASGITransport`を利用する
* 仮想環境のpytestを利用するため、`python -m pytest`で実行すると確実である

ライブラリはメジャーバージョンアップ時にAPIや推奨実装が変更されることがあるため、導入手順と合わせて検証環境のバージョンを記録しておくことで、将来の再現性向上やトラブルシューティングに役立ちます。
