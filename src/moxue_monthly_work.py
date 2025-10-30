
import os
from datetime import datetime, timedelta

import pandas as pd

key = "moxue"
folder_path = rf"D:\monthly\{key}"
filter_key = "墨雪官方旗舰店"
output_filename = f"{filter_key}：{(datetime.now() - timedelta(days=30)).month}月1日-{datetime.now().month}月1日.xlsx"

def _get_fils() -> list:
    """
    获取到所有的excel文件
    :return:
    """
    all_files = os.listdir(folder_path)

    dfs = []
    for file in all_files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)
        dfs.append(df)
        print(f"已读取：{file}, 行：{len(df)}")
    return dfs

def _filtering() -> list:
    """
    对表格当中的列：达人昵称，来进行过滤
    :return:
    """
    dfs = _get_fils()
    fdfs = []
    for df in dfs:
        filtered_df = df[df["达人昵称"] == filter_key]
        fdfs.append(filtered_df)
    return fdfs

def merge() -> None:
    """
    把所有的表格合并成为新的表格
    :return:
    """
    filtered_fdfs = _filtering()
    merged_df = pd.concat(filtered_fdfs, ignore_index=True)

    output_path = os.path.join(os.path.dirname(folder_path), output_filename)
    merged_df.to_excel(output_path, index=False)
    print("执行完毕")

if __name__ == '__main__':
    merge()