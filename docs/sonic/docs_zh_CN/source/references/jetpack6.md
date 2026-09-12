# G1 JetPack 6 刷机指南

## 1. 下载镜像

1. **下载所需文件** —— 从 [Jetpack 6.2](https://drive.google.com/drive/folders/1ho17ectOxi7FbaRFdpAbP4tet8BJWjbm) 获取 `.tar` 文件与镜像文件。

## 2. 拆下 Orin NX 的 NVMe

### 拆除 NVMe SSD 的步骤

1. **拆下背部把手螺丝**

   使用 5 mm T 形内六角扳手，拧下机器人背部靠近把手处的两颗螺丝。

2. **拆下海绵与塑料背板**

   - 使用 Fanttik 工具包中的 2 mm 内六角工具，拧下固定海绵与塑料背板的四颗螺丝。
   - 掀开背板，露出内部组件。

```{image} ../_static/screws.png
:width: 600px
:align: center
```

3. **拧下 Orin NX 模块上的 NVMe 螺丝**

   使用十字螺丝刀（同样在 Fanttik 工具包中）拧下固定 Orin NX 的 NVMe SSD 的那一颗螺丝。

```{image} ../_static/ssd.png
:width: 600px
:align: center
```

4. **取出 SSD 卡**

   小心地将 NVMe SSD 从插槽中滑出并取下。

## 3. 刷写 NVMe SSD

**将 Orin NX 上的 NVMe SSD 装入 NVMe SSD 硬盘盒适配器。**
（从笔记本电脑烧录镜像时需要硬盘盒）

1. 确认机器人的 SSD 已卸载。运行以下命令，确保外接 SSD（即将烧录镜像的盘）未挂载：

```bash
sudo umount /dev/sda*
```

2. 如果该 SSD 之前处于挂载状态，此命令会将其安全卸载，使其可以开始写入镜像。

3. 进入存放镜像的文件夹（`cd robot_NXUpgrade/`），然后运行以下命令：

```bash
bzip2 -dc g1-nx-j6.2.img.bz2 | sudo dd of=/dev/sda bs=4M status=progress conv=fsync
```

4. 完成后，使用以下命令弹出该卡，以便安全拔出：

```bash
sudo sync
sudo udisksctl power-off -b /dev/sda
```

5. **将 SSD 卡放到一旁，继续刷机流程的第二部分！**

## 4. 让机器人进入刷机模式

1. **给 G1 上电**，等待三盏电源指示灯全部常亮。

2. **使用 USB-C 线缆将机器人连接到你的笔记本电脑/台式机。**

3. **同时按住机器人上的两个白色按钮**，持续两秒。

4. 在仍按住它们的同时，**松开上面的白色按钮**，继续按住**下面的按钮** 2 秒，直到**三盏绿灯变为两盏绿灯**。

```{image} ../_static/flashing.png
:width: 600px
:align: center
```

5. 当只剩两盏灯亮起时，机器人**此时已处于刷机模式**。在电脑上打开一个新终端并输入 `lsusb`。你应该能看到包含 `NVIDIA Corp. APX` 的文本。

6. 现在可以继续运行以下命令：

```bash
sudo tar -xjvf Jetpack_6.2_nx.tar.bz2
cd Jetpack_6.2_nx/Linux_for_Tegra
sudo ./flash_nx_module.sh
```

耐心等待约 8 分钟，直到显示成功。

## 5. 重新组装机器人

1. 刷机完成后，**关闭机器人电源**。

2. **将 Orin NX 的 NVMe SSD 重新装回** G1 机器人上的插槽，并用螺丝固定。

3. **装回海绵与塑料背板**，使用与拆除时相同的工具。

4. **拧紧所有螺丝**，确保背板与把手牢固到位。

5. 使用以下命令在 Jetson Orin 上开启 `maxn` 模式：


```
sudo nvpmodel -m 0
```

然后使用


```
sudo jetson_clocks
sudo jetson_clocks --show  
```

检查是否已处于 Maxn 模式。

## 6. 安装所需的 JetPack 软件包

安装部署所需的软件包：

```
sudo apt-get install -y nvidia-l4t-dla-compiler libcudla-dev-12-6
```
