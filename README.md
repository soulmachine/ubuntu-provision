# Ubuntu 一键装机

基本思路是使用 Ansible 来自动化所有操作。

## 1. 前期准备


### 1.1 安装 pip

Ubuntu 16.04 自带了 Python 2.7 和 Python 3.5，所以不需要安装 Python, 但是默认没有 pip， 所以我们需要安装 pip 。 Ansible 目前只能与 Python 2.7 兼容，所以我们只需要给 Python 2.7 安装 pip，千万不要误安装了 `python3-pip`

    sudo apt-get -qy install python-pip


### 1.2 安装 Ansible

    sudo -H pip install --upgrade pip
    sudo apt-get -qy install libssl-dev
    sudo -H pip install ansible

用 `sudo apt-get install ansible` 也可以安装，但是 apt源里的 ansible 版本一般会比较之后，用 pip 方式安装的版本会新一点。


## 2. 执行 playbook 开始一键装机

    ansible-playbook -i localhost, -vv all.yml


或者只安装深度学习相关的框架，

    ansible-playbook -i localhost, -vv deep-learning.yml


几个 playbook 的用途说明：

* `all.yml` 用来安装所有
* `deep-learning.yml` 用来安装所有深度学习相关的工具，例如 TensorFlow, Caffe, Torch 等
* `cuda.yml` 用于安装 Nvidia 显卡驱动，CUDA 和 cuDNN
* `tensorflow.yml` 是用来构建TensorFlow开发环境的
* `caffe.yml` 用于安装 Caffe 开发环境
* `torch.yml` 用于安装 Torch 开发环境
* `mxnet.yml` 用于安装 mxnet 开发环境
* `r.yml` 用于安装 R, RStudio
* `spark.yml` 用于安装 local 模式的 Apache Spark

