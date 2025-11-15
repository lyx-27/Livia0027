# Solana Token Holders 追踪工具使用说明

## 文件说明

1. **main.py** - 主程序文件，负责协调API调用、数据处理和Excel操作
2. **solana_tracker_api.py** - API调用模块，负责从Solana Tracker获取Top Holders数据
3. **config.py** - 配置文件，包含您的API Key

## 环境要求

- Python 3.6+
- 需要安装以下Python库：
  ```bash
  pip install requests openpyxl
  ```

## 使用方法

### 基本用法

在命令行中运行以下命令：

```bash
python3 main.py <代币地址> <Excel文件名>
```

### 示例

```bash
# 追踪USDC代币的Top Holders，数据保存到 usdc_holders.xlsx
python3 main.py EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v usdc_holders.xlsx

# 追踪另一个代币，数据保存到 my_token.xlsx
python3 main.py 另一个代币地址 my_token.xlsx
```

## 程序功能

1. **自动创建/更新Excel文件**：程序会自动创建指定名称的Excel文件，或更新现有文件，包含两个工作表：
   - `Token_Tracking`：记录每次抓取的Top Holders数据，**包含钱包地址和持有百分比**
   - `Wallet_Changes`：记录钱包地址的变化，**包含新增/移除钱包地址和其对应的持有百分比**

2. **单次抓取**：每次运行脚本，都会进行一次Top Holders数据的抓取，并将其作为新的一列添加到Excel文件中。

3. **变化高亮**：与上一次抓取相比，新增的钱包地址会用黄色高亮显示。

4. **变化记录**：所有钱包地址的新增和移除都会记录在`Wallet_Changes`工作表中。

## Excel文件结构

### Token_Tracking 工作表
- **A1**: "代币地址:"
- **B1**: 您输入的代币地址
- **A3**: "时间戳"
- **B3及以后**: 每次抓取的时间戳
- **A4及以后**: 每次抓取对应的Top Holders数据（格式：`钱包地址 (持有百分比%)`）

### Wallet_Changes 工作表
- **A列**: 抓取时间
- **B列**: 新增钱包地址（格式：`钱包地址 (持有百分比%)`）
- **C列**: 移除钱包地址（格式：`钱包地址 (持有百分比%)`）

## 注意事项

1. **API限制**：Solana Tracker免费版每月有10,000次请求限制，每秒1次请求限制。
2. **网络连接**：确保网络连接稳定，避免API调用失败。
3. **文件权限**：确保程序有权限在当前目录创建和修改Excel文件。

## 故障排除

1. **API调用失败**：检查网络连接和API Key是否正确。
2. **Excel文件无法创建**：检查文件权限和磁盘空间。

## 多代币追踪

如果您想同时追踪多个代币，可以为每个代币运行一个单独的程序实例，使用不同的Excel文件名：

```bash
# 终端1
python3 main.py 代币地址1 token1_holders.xlsx

# 终端2  
python3 main.py 代币地址2 token2_holders.xlsx
```

## API Key 更新

如果需要更新API Key，请编辑 `config.py` 文件中的 `SOLANA_TRACKER_API_KEY` 变量。

