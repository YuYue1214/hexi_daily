import pandas as pd


def split_large_excel(input_file, output_prefix, chunk_size=65000):
    """
    将大Excel文件按指定行数拆分成多个小文件

    Args:
        input_file (str): 输入文件路径（如 "赫系官旗订单.xlsx"）
        output_prefix (str): 输出文件前缀（如 "赫系订单_"）
        chunk_size (int): 每个文件的行数（默认6.5万）
    """
    # 读取原始文件（支持.xlsx或.csv）
    df = pd.read_excel(input_file)  # 如果是csv，用 pd.read_csv()

    # 计算需要拆分的文件数量
    total_rows = len(df)
    num_files = (total_rows // chunk_size) + (1 if total_rows % chunk_size else 0)

    # 按chunk_size拆分并保存
    for i in range(num_files):
        start = i * chunk_size
        end = start + chunk_size
        chunk = df.iloc[start:end]

        # 输出文件名（如 "赫系订单_1.xlsx"）
        output_file = f"{output_prefix}{i + 1}.xlsx"
        chunk.to_excel(output_file, index=False)
        print(f"已生成: {output_file} (行数: {len(chunk)})")

    print(f"\n拆分完成！共生成 {num_files} 个文件，每文件最多 {chunk_size} 行。")


# 使用示例
if __name__ == "__main__":
    split_large_excel(
        input_file=r"D:\monthly\赫系官方旗舰店：5月1日-6月1日.xlsx",  # 替换为实际文件名
        output_prefix="赫系订单_",  # 输出文件前缀
        chunk_size=65000  # 每文件6.5万行
    )