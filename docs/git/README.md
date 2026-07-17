# VSCodeでGit履歴を確認・整理する

VSCodeの拡張機能を使ってGit履歴を見やすくし、コミットの取り消しや履歴整理を安全に行うための手順をまとめる。
ローカルの修正を残したい場合、コミットだけを消したい場合、リモートへpush済みの場合で使うコマンドを分けて判断できるようにする。

## できること

- VSCode上でコミット履歴、差分、ブランチの流れを確認しやすくする
- 直近コミットを、作業ファイルを残したまま取り消す
- 誤って作成したコミットをinteractive rebaseで履歴から除外する
- push済み履歴を書き換える前に、影響範囲と安全なpush方法を確認する

## 前提条件

- Gitがインストール済みであること
- VSCodeがインストール済みであること
- 対象ディレクトリがGitリポジトリであること
- リモートへpushする場合は、対象リポジトリへのpush権限があること

## 全体像

| 場所・役割 | やること |
| --- | --- |
| VSCode | 拡張機能で履歴、差分、ブランチを確認する |
| ローカルリポジトリ | `reset` や `rebase` でコミット履歴を整理する |
| リモートリポジトリ | 必要な場合だけ `--force-with-lease` で履歴を書き換える |

## 手順

### 1. VSCodeにGit補助拡張を追加する

Gitの履歴やブランチ関係を視覚的に確認しやすくするため、VSCodeに拡張機能を追加する。

- [GitLens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens)
- [Git Graph](https://marketplace.visualstudio.com/items?itemName=mhutchie.git-graph)

### 2. 現在の状態を確認する

履歴を直す前に、作業ツリーとリモートとの差分を確認する。
未保存の変更や他人のpushがある状態で履歴を書き換えると、意図しない差分を巻き込むことがある。

```sh
git status
git branch --show-current
git log --oneline --decorate --graph -10
```

リモートブランチとの差分も見たい場合は、先に最新の参照を取得する。

```sh
git fetch
git log --oneline --decorate --graph HEAD..@{u}
git log --oneline --decorate --graph @{u}..HEAD
```

### 3. 目的に合う取り消し方法を選ぶ

作業ファイルを残したいのか、コミット履歴から消したいのか、push済みなのかで使うコマンドを分ける。

| やりたいこと | 使う操作 |
| --- | --- |
| 直近コミットだけ取り消し、変更内容は残す | `git reset --soft HEAD~1` |
| 直近コミットだけ取り消し、変更内容を未ステージに戻す | `git reset HEAD~1` |
| 複数コミットの順序変更・削除・統合をする | `git rebase -i` |
| push済み履歴をリモートにも反映する | `git push --force-with-lease` |

## 設定値の意味

| 項目 | 例 | 説明 |
| --- | --- | --- |
| `HEAD~1` | `git reset --soft HEAD~1` | 現在のコミットから1つ前を指す |
| `HEAD~3` | `git rebase -i HEAD~3` | 直近3コミットを編集対象にする |
| `@{u}` | `git log HEAD..@{u}` | 現在のブランチのupstreamを指す |
| `--soft` | `git reset --soft HEAD~1` | コミットだけを戻し、変更内容はステージ済みのまま残す |
| `--force-with-lease` | `git push --force-with-lease` | リモートが想定外に進んでいた場合はpushを拒否する |

## よくある構成

### 直近コミットを取り消して、修正内容は残す

プルしてからコミットしたかった、コミットメッセージや含めるファイルを直したい、という場合に使う。

```sh
git reset --soft HEAD~1
```

実行後、変更内容はステージ済みの状態で残る。
ステージを外したい場合は次を実行する。

```sh
git restore --staged .
```

### 誤って作成したコミットを履歴から除外する

直近数コミットの中から特定のコミットを消したい場合はinteractive rebaseを使う。

```sh
git rebase -i HEAD~3
```

エディタが開いたら、取り消したいコミットの行を `drop` に変更して保存する。
GitLensを入れている場合は、VSCode上のInteractive Rebase画面から同じ操作ができる。

#### 派生：過去のコミットを分割する

エディタが開いたら、分割したいコミットの行を `edit` に変更して保存する。
その後、当該コミットを変更状態に戻す。

```sh
git reset @^
```

一つ前のコミットに含めたい場合は`git commit --amend`、分割したい場合は`git commit`を実行する。

### push済みの履歴を書き換える

push済みコミットを `reset` や `rebase` で書き換えた場合、通常のpushは拒否される。
チームで共有しているブランチでは、先に関係者へ確認してから実行する。

```sh
git push --force-with-lease
```

`--force-with-lease` は、リモートブランチが自分の把握していないコミットを含む場合にpushを止める。
単純な `--force` より事故を起こしにくいため、履歴を書き換えるpushではこちらを基本にする。

### 作業中の変更を一時退避してから履歴を直す

未コミットの変更があるまま履歴を直すと、rebaseやresetの判断が難しくなる。
必要に応じて一時退避する。

```sh
git stash push -m "before history cleanup"
```

履歴整理後、退避した変更を戻す。

```sh
git stash pop
```

## トラブルシューティング

### rebase中にコンフリクトした

- `git status` で競合ファイルを確認する
- ファイルを修正して `git add <ファイル>` を実行する
- 続行する場合は `git rebase --continue` を実行する
- 中止して元に戻す場合は `git rebase --abort` を実行する

### pushが拒否された

- `git fetch` でリモートの最新状態を取得する
- `git log --oneline --decorate --graph --all -20` で分岐状態を確認する
- 他人のコミットが進んでいる場合は、履歴を書き換えてよいか確認する
- 問題なければ `git push --force-with-lease` を使う

### 消したコミットを戻したい

- `git reflog` で過去の `HEAD` の位置を探す
- 戻したいコミットを確認する
- 必要に応じて `git cherry-pick <コミットID>` で取り戻す

```sh
git reflog
git cherry-pick <コミットID>
```

## 運用メモ

- 共有ブランチの履歴を書き換える前に、必ず影響範囲を確認する
- `git push --force` は原則使わず、`git push --force-with-lease` を使う
- 作業前に `git status` と `git log --oneline --decorate --graph -10` を確認する
- 不安な場合は、作業前の位置に一時ブランチを作る

```sh
git branch backup/before-history-cleanup
```

## 参考リンク

- [Git Documentation](https://git-scm.com/doc)
- [Git - git-reset Documentation](https://git-scm.com/docs/git-reset)
- [Git - git-rebase Documentation](https://git-scm.com/docs/git-rebase)
