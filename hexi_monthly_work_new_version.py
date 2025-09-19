import os
from concurrent.futures import ThreadPoolExecutor
import math

import pandas as pd
from pandas import DataFrame

key = "hexi"
folder_path = fr"D:\monthly\{key}"
# filter_key = "赫系官方旗舰店星品"
filter_key = "赫系官方旗舰店"
# output_filename = f"{filter_key}：{(datetime.now() - timedelta(days=30)).month}月1日-{datetime.now().month}月1日.xlsx"
output_filename = "旗舰店.xlsx"
# output_filename = "星品.xlsx"
chunk_size = 50000
max_rows_per_sheet = 65000  # 每个工作表的最大行数


def _process_file(file_path: str) -> DataFrame:
    """
    处理单个文件，返回筛选之后的DataFrame
    :return:
    """
    filtered_chunks = []
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        filtered_chunk = chunk[chunk["达人昵称"] == filter_key]
        print(f"已读取：{file_path}, 行：{len(filtered_chunk)}")
        filtered_chunks.append(filtered_chunk)
    return pd.concat(filtered_chunks, axis=0)


def split_dataframe_to_sheets(df: DataFrame, max_rows: int) -> dict:
    """
    将DataFrame分割成多个不超过max_rows的子DataFrame
    返回字典：{sheet_name: df}
    """
    total_rows = len(df)
    num_sheets = math.ceil(total_rows / max_rows)
    sheets = {}
    for i in range(num_sheets):
        start = i * max_rows
        end = start + max_rows
        sheet_name = f"数据_{i + 1}"
        sheets[sheet_name] = df.iloc[start:end]
    return sheets


def do_merge() -> None:
    """
    进行预处理之后进行合并，并将结果分割成多个工作表保存到一个Excel文件
    :return:
    """
    # 获取所有文件路径
    file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path)]

    # 多线程处理文件
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(_process_file, file_paths))

    # 合并所有结果
    final_df = pd.concat(results, axis=0)

    # 分割DataFrame到多个工作表
    sheets = split_dataframe_to_sheets(final_df, max_rows_per_sheet)

    # 输出路径
    output_path = os.path.join(os.path.dirname(folder_path), output_filename)

    # 写入Excel文件（多个工作表）
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for sheet_name, sheet_data in sheets.items():
            sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"已写入工作表: {sheet_name}, 行数: {len(sheet_data)}")

    print(f"执行完成，文件已保存到: {output_path}")


if __name__ == '__main__':
    do_merge()