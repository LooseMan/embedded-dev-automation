# Ansible 制御ノードのセットアップ（macOS 15）

このリポジトリの `ansible/` は、macOS 15 から AlmaLinux 10（`192.168.56.5`）を踏み台にし、NAT 配下のゲストへ接続する構成です。inventory にはこの接続先と踏み台が設定済みです。

## 1. 開発ツールと Homebrew を準備する

macOS の Command Line Tools を導入します。ダイアログが表示されたら、案内に従ってインストールを完了してください。

```bash
xcode-select --install
```

次に Homebrew を確認します。未導入の場合は [Homebrew 公式サイト](https://brew.sh/)の手順で導入してから、以降を実行してください。

```bash
brew --version
brew update
```

## 2. Ansible を導入する

```bash
brew install ansible sshpass
ansible --version
```

導入例（2026/07/12時点の最新バージョンをインストールした場合）

```bash
<ユーザ>@<ホスト> simple-libvirt-vm % ansible --version
ansible [core 2.21.1]
  config file = None
  configured module search path = ['/Users/<ユーザ>/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /usr/local/Cellar/ansible/14.1.0/libexec/lib/python3.14/site-packages/ansible
  ansible collection location = /Users/<ユーザ>/.ansible/collections:/usr/share/ansible/collections
  executable location = /usr/local/bin/ansible
  python version = 3.14.6 (main, Jun 10 2026, 10:03:53) [Clang 17.0.0 (clang-1700.6.4.2)] (/usr/local/Cellar/ansible/14.1.0/libexec/bin/python)
  jinja version = 3.1.6
  pyyaml version = 6.0.3 (with libyaml v0.2.5)
<ユーザ>@<ホスト> simple-libvirt-vm % 
```

## 3. SSH 鍵と接続先を確認する

Terraform と Ansible は同じ秘密鍵を使用します。鍵ファイルが存在し、所有者だけが読める権限になっていることを確認します。

```bash
test -f ~/.ssh/id_ed25519
chmod 600 ~/.ssh/id_ed25519
ssh -i ~/.ssh/id_ed25519 ifour@192.168.56.5 'hostname'
```

この構成では次の値を使用します。接続先・認証情報・踏み台を変更する場合は、`inventory/hosts.yml` を更新してください。

| 用途 | 設定 |
| --- | --- |
| ゲスト | `192.168.151.10`（ユーザー／パスワード: `vagrant`／`vagrant`） |
| 踏み台 | `ifour@192.168.56.5` |
| 秘密鍵 | `~/.ssh/id_ed25519` |
| inventory | `inventory/hosts.yml` |
| playbook | `playbook/playbook.yml` |

## レガシー OS 向け接続変数

`inventory/hosts.yml` は、通常の SSH クライアントでは既定で拒否される RHEL/CentOS 5 系の SSH サーバーへ接続するため、次の変数を設定しています。

```yaml
nested_guest_vm_2:
  ansible_host: 192.168.151.10
  ansible_user: vagrant
  ansible_password: vagrant

ansible_ssh_common_args: >-
  -o KexAlgorithms=+diffie-hellman-group14-sha1
  -o HostKeyAlgorithms=+ssh-rsa
  -o PubkeyAcceptedAlgorithms=+ssh-rsa
  -o StrictHostKeyChecking=no
  -o ProxyCommand="ssh -W %h:%p -l ifour -i /Users/arakimasaya/.ssh/id_ed25519 192.168.56.5"
```

| 設定 | 役割 |
| --- | --- |
| `ansible_host` | Ansible が接続するゲストの NAT 側 IP アドレスです。`ProxyCommand` がこのアドレスへの通信を踏み台へ転送します。 |
| `ansible_user` | ゲストへの SSH ログインユーザーです。このイメージでは `vagrant` を使用します。 |
| `ansible_password` | ゲストの SSH パスワードです。パスワード認証には制御ノード側の `sshpass` が必要なため、`brew install ansible sshpass` としています。 |
| `KexAlgorithms=+diffie-hellman-group14-sha1` | 鍵交換方式を追加します。ゲストが提示する SHA-1 ベースの方式のうち、`group1` より強い `group14` だけを許可しています。 |
| `HostKeyAlgorithms=+ssh-rsa` | ゲストが提示する RSA/SHA-1 の**ホスト鍵**を受け入れます。未指定の場合、macOS の新しい OpenSSH はこの鍵を拒否します。 |
| `PubkeyAcceptedAlgorithms=+ssh-rsa` | RSA/SHA-1 による**公開鍵ユーザー認証**を許可します。現在のゲスト接続はパスワード認証ですが、公開鍵認証へ切り替える場合にも必要になることがあります。 |
| `StrictHostKeyChecking=no` | 初回接続時にホスト鍵の確認を求めずに接続します。検証済みの環境では、ホスト鍵を `known_hosts` に登録してこの設定を削除する方が安全です。 |
| `ProxyCommand` | `ifour@192.168.56.5` を踏み台として使います。`%h` と `%p` は Ansible が接続しようとしたゲストの IP とポートに置き換えられ、`ssh -W` がその TCP 接続を中継します。踏み台への認証には `~/.ssh/id_ed25519` を使います。 |

これらの弱い暗号方式と `StrictHostKeyChecking=no` は、`old_servers` グループ内のレガシーゲストだけに限定しています。ほかのホストや `all:vars` には配置しないでください。また、`ansible_password` は平文で保持されるため、共有リポジトリで使用する場合は Ansible Vault などで暗号化してください。

## 4. inventory と SSH 経路を確認する

`ansible` ディレクトリで次を実行します。最初のコマンドでは inventory が `nested_guest_vm_2` を認識していること、次のコマンドでは踏み台を経由してゲスト上でコマンドを実行できることを確認します。

```bash
$ cd ansible
$ ansible-inventory -i inventory/hosts.yml --graph
@all:
  |--@ungrouped:
  |--@old_servers:
  |  |--nested_guest_vm_2
$ ansible -i inventory/hosts.yml all -m raw -a 'id'
nested_guest_vm_2 | CHANGED | rc=0 >>
uid=500(vagrant) gid=500(vagrant) 所属グループ=500(vagrant)
Shared connection to 192.168.151.10 closed.
```

`raw` はリモート側の Python を使わないため、RHEL/CentOS 5 系への SSH 経路だけを確認する用途に適しています。初回はホスト鍵登録を確認するプロンプトが出ることがあります。

RHEL/CentOS 5 系のために追加している SSH 設定の詳細は、前節「レガシー OS 向け接続変数」を参照してください。

## 5. playbook を実行する

VM の起動後、SSH が利用可能になったら実行します。RHEL/CentOS 5 の標準 Python 2.4 でも動くよう、playbook は Python を必要としない `raw` タスクで接続確認とネットワーク設定を行います。

ホストオンリー NIC の MAC アドレスは Terraform で指定せず、libvirt に重複しない値を自動割り当てさせます。そのため `ifcfg-eth1` にも `HWADDR` は記載せず、ベースイメージの `eth0` に対して Terraform が追加する 2 枚目の NIC（`eth1`）へ設定を適用します。

```bash
ansible-playbook \
  -i inventory/hosts.yml \
  playbook/playbook.yml
```

`--check` を付けると、Python 不要の SSH 接続確認と `eth1` の存在確認だけを実行し、ネットワーク設定は変更しません。

> **RHEL 5 系の Python に関する注意:** 標準の RHEL/CentOS 5 は Python 2.4 です。現行の Ansible はこのバージョンを管理対象としてサポートしておらず、`ping` や `shell` などの通常モジュールは失敗します。この playbook のレガシーゲスト向けタスクでは `raw` を使用しています。通常モジュールを追加する場合は、ゲストに対応する Python を用意するか、同様に `raw` で実装してください。
