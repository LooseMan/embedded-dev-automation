FROM almalinux:9

# 1. OS更新（ほぼ固定）
RUN dnf -y update

# 2. リポジトリ追加（ほぼ固定）
RUN dnf -y install epel-release

# 3. パッケージインストール（たまに更新）
RUN dnf -y install \
        ansible \
        python3-winrm \
        openssh-clients \
        rsync \
        crypto-policies-scripts && \
    dnf clean all

# 4. システム設定（固定）
RUN update-crypto-policies --set DEFAULT:SHA1

# 5. Ansible 設定（ほぼ固定）
COPY ansible.cfg /etc/ansible/ansible.cfg

# 6. 作業ディレクトリ（固定）
WORKDIR /workspace

# 7. デフォルト起動（固定）
CMD ["/bin/bash"]
