# Ubuntu 一键装机

基本思路是使用 Ansible 来自动化所有操作。

## 1. 前期准备


### 1.1 安装 pip

Ubuntu 16.04 自带了 Python 2.7 和 Python 3.5，所以不需要安装 Python, 但是默认没有 pip， 所以我们需要安装 pip 。 Ansible 目前只能与 Python 2.7 兼容，所以我们只需要给 Python 2.7 安装 pip，千万不要误安装了 `python3-pip`

    sudo apt-get -qy install python-pip


### 1.2 安装 Ansible

    sudo pip install --upgrade pip
    sudo apt-get -qy install libssl-dev
    sudo pip install ansible

用 `sudo apt-get install ansible` 也可以安装，但是 apt源里的 ansible 版本一般会比较之后，用 pip 方式安装的版本会新一点。


## 2. 执行 playbook 开始一键装机

    ansible-playbook -i localhost, -vv all.yml

`playbook.yml` 主要是安装一些最常见的工具。

本项目还有其他几个 playbook, 

* `tensorflow.yml` 是用来构建TensorFlow开发环境的，会自动化安装 Nvidia 驱动, CUDA, TensorFlow 等软件包
* `r.yml` 用于安装 R, RStudio
* `spark.yml` 用于安装 local 模式的 Apache Spark

