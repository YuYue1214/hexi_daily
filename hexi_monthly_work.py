import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import pandas as pd
from pandas import DataFrame

key = "hexi"
folder_path = fr"D:\monthly\{key}"
filter_key = "赫系官方旗舰店"
output_filename = f"{filter_key}：{(datetime.now() - timedelta(days=30)).month}月1日-{datetime.now().month}月1日.xlsx"

chunk_size = 50000

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

def do_merge() -> None:
    """
    进行预处理之后进行合并
    :return:
    """
    file_paths = []
    for file in os.listdir(folder_path):
        file_paths.append(os.path.join(folder_path, file))

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(_process_file, file_paths))

    final_df = pd.concat(results, axis=0)

    output_path = os.path.join(os.path.dirname(folder_path), output_filename)
    final_df.to_excel(output_path, index=False)
    print("执行完成")



if __name__ == '__main__':
    do_merge()