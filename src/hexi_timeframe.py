import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

folder_path = r"D:\monthly\hexi_timeframe"
chunk_size = 50000  # 分块读取大小
file_processing_workers = 4  # 文件处理的线程数

# 只读取需要的列
required_columns = ['订单提交时间', '订单应付金额', '售后状态', '取消原因']


def _get_file_paths() -> list:
    """
    获取所有需要读取的文件路径
    :return: 文件路径列表
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")

    all_files = os.listdir(folder_path)
    excel_files = [f for f in all_files if f.endswith(('.xlsx', '.xls'))]
    csv_files = [f for f in all_files if f.endswith('.csv')]

    files_to_read = excel_files if excel_files else csv_files
    return [os.path.join(folder_path, file) for file in files_to_read]


def _read_excel_file(file_path: str) -> list:
    """
    读取Excel文件的所有工作表，只读取需要的列
    :param file_path: 文件路径
    :return: DataFrame列表
    """
    dfs = []
    file_name = os.path.basename(file_path)

    try:
        # 获取所有工作表名称
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names

        for sheet_name in sheet_names:
            try:
                # 只读取需要的列
                df = pd.read_excel(file_path, sheet_name=sheet_name, usecols=required_columns)
                if not df.empty:
                    dfs.append(df)
                    print(f"已读取：{file_name} - 工作表：{sheet_name}, 行：{len(df)}")
            except Exception as e:
                # 如果某个工作表缺少列，尝试读取所有列然后筛选
                try:
                    df_all = pd.read_excel(file_path, sheet_name=sheet_name)
                    # 检查是否有需要的列
                    missing_cols = [col for col in required_columns if col not in df_all.columns]
                    if missing_cols:
                        print(f"警告：{file_name} - {sheet_name} 缺少列：{missing_cols}，跳过")
                        continue
                    df = df_all[required_columns]
                    if not df.empty:
                        dfs.append(df)
                        print(f"已读取：{file_name} - 工作表：{sheet_name}, 行：{len(df)}")
                except Exception as e2:
                    print(f"读取工作表失败 {file_name} - {sheet_name}: {e2}")
                    continue

    except Exception as e:
        print(f"读取文件失败 {file_name}: {e}")
        return []

    return dfs


def _read_csv_file(file_path: str) -> list:
    """
    分块读取CSV文件，只读取需要的列
    :param file_path: 文件路径
    :return: DataFrame列表
    """
    dfs = []
    file_name = os.path.basename(file_path)

    try:
        # 先读取第一行检查列名
        first_chunk = pd.read_csv(file_path, nrows=1)
        missing_cols = [col for col in required_columns if col not in first_chunk.columns]
        if missing_cols:
            print(f"警告：{file_name} 缺少列：{missing_cols}，跳过")
            return []

        # 分块读取
        for chunk in pd.read_csv(file_path, chunksize=chunk_size, usecols=required_columns):
            if not chunk.empty:
                dfs.append(chunk)

        if dfs:
            total_rows = sum(len(df) for df in dfs)
            print(f"已读取：{file_name}, 行：{total_rows}")

    except Exception as e:
        print(f"读取文件失败 {file_name}: {e}")
        return []

    return dfs


def _process_file(file_path: str) -> list:
    """
    处理单个文件（Excel或CSV）
    :param file_path: 文件路径
    :return: DataFrame列表
    """
    if file_path.endswith(('.xlsx', '.xls')):
        return _read_excel_file(file_path)
    elif file_path.endswith('.csv'):
        return _read_csv_file(file_path)
    else:
        return []


def _get_files() -> list:
    """
    使用多线程读取所有文件
    :return: DataFrame列表
    """
    file_paths = _get_file_paths()
    if not file_paths:
        print("未找到任何文件")
        return []

    all_dfs = []

    # 使用多线程并行读取文件
    with ThreadPoolExecutor(max_workers=file_processing_workers) as executor:
        future_to_file = {executor.submit(_process_file, file_path): file_path for file_path in file_paths}

        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                dfs = future.result()
                all_dfs.extend(dfs)
            except Exception as e:
                print(f"处理文件失败 {os.path.basename(file_path)}: {e}")

    return all_dfs


def _parse_time(time_str):
    """
    解析时间字符串
    :param time_str: 时间字符串
    :return: datetime对象，解析失败返回None
    """
    if pd.isna(time_str) or time_str == '':
        return None

    # 去除制表符和空格
    time_str = str(time_str).strip().replace('\t', '')

    try:
        return pd.to_datetime(time_str)
    except:
        return None


def _filtering(dfs) -> list:
    """
    过滤有效订单
    去除"售后状态"和"取消原因"这两个字段当中有值的数据
    :return:
    """
    fdfs = []
    for df in dfs:
        # 售后状态为空或为"-"
        after_sale_mask = (
                df['售后状态'].isna() |
                (df['售后状态'] == '') |
                (df['售后状态'] == '-')
        )
        # 取消原因为空
        cancel_mask = (
                df['取消原因'].isna() |
                (df['取消原因'] == '')
        )
        # 两个条件都满足的数据才是有效订单
        valid_mask = after_sale_mask & cancel_mask
        filtered_df = df[valid_mask]
        fdfs.append(filtered_df)
    return fdfs


def _get_date_timeframe(dt):
    """
    获取日期和时段标识（10分钟间隔）
    例如：日期 "2025-11-14", 时段 "06:00-06:10"
    """
    if dt is None:
        return None, None

    # 获取日期
    date_str = dt.strftime("%Y-%m-%d")

    # 获取时段
    hour = dt.hour
    minute = dt.minute

    # 计算10分钟间隔的起始分钟
    start_minute = (minute // 10) * 10
    end_minute = start_minute + 10

    start_time = f"{hour:02d}:{start_minute:02d}"
    if end_minute >= 60:
        end_hour = hour + 1
        end_minute = 0
        end_time = f"{end_hour:02d}:{end_minute:02d}"
    else:
        end_time = f"{hour:02d}:{end_minute:02d}"

    timeframe_str = f"{start_time}-{end_time}"
    return date_str, timeframe_str


def _calculate_timeframe(df):
    """
    计算每天的各个时段的订单应付金额统计
    """
    # 解析时间
    df['parsed_time'] = df['订单提交时间'].apply(_parse_time)

    # 过滤掉时间解析失败的数据
    valid_time_df = df[df['parsed_time'].notna()].copy()

    # 添加日期和时段标识
    date_timeframe = valid_time_df['parsed_time'].apply(_get_date_timeframe)
    valid_time_df['日期'] = date_timeframe.apply(lambda x: x[0] if x[0] else None)
    valid_time_df['时段'] = date_timeframe.apply(lambda x: x[1] if x[1] else None)

    # 过滤掉日期或时段为None的数据
    valid_time_df = valid_time_df[(valid_time_df['日期'].notna()) & (valid_time_df['时段'].notna())].copy()

    # 确保订单应付金额是数值类型
    valid_time_df['订单应付金额'] = pd.to_numeric(valid_time_df['订单应付金额'], errors='coerce')

    # 按日期和时段分组，累加订单应付金额
    timeframe_stats = valid_time_df.groupby(['日期', '时段']).agg({
        '订单应付金额': ['sum', 'count']
    }).reset_index()

    # 重命名列
    timeframe_stats.columns = ['日期', '时段', '累计金额', '订单数量']

    # 按日期和时段排序
    timeframe_stats['日期排序键'] = pd.to_datetime(timeframe_stats['日期'])
    timeframe_stats['时段排序键'] = timeframe_stats['时段'].apply(
        lambda x: int(x.split(':')[0]) * 60 + int(x.split('-')[0].split(':')[1])
    )
    timeframe_stats = timeframe_stats.sort_values(['日期排序键', '时段排序键']).drop(['日期排序键', '时段排序键'], axis=1)

    return timeframe_stats


def timeframe() -> None:
    """
    生成时段统计报告
    """
    # 获取所有文件
    dfs = _get_files()

    # 过滤有效订单
    filtered_dfs = _filtering(dfs)

    # 合并所有数据
    merged_df = pd.concat(filtered_dfs, ignore_index=True)

    # 计算时段统计
    timeframe_stats = _calculate_timeframe(merged_df)

    # 生成输出文件路径
    output_filename = "时段统计.xlsx"
    output_path = os.path.join(os.path.dirname(folder_path), output_filename)

    # 保存到Excel
    timeframe_stats.to_excel(output_path, index=False)
    print("执行完毕")
    print(f"共统计 {len(timeframe_stats)} 个时段")
    print(f"总订单数: {timeframe_stats['订单数量'].sum()}")
    print(f"总金额: {timeframe_stats['累计金额'].sum():.2f}")


if __name__ == '__main__':
    timeframe()
