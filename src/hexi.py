import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import math
from typing import Dict, List, Tuple, Set
from collections import defaultdict
from datetime import datetime
import shutil

import pandas as pd
from pandas import DataFrame

# 导入飞书相关模块
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ext.feishu.file import upload_file, FileType
from ext.feishu.message import send_file, ReceiveIdType
from ext.feishu.token import get_tenant_access_token
from ext.feishu.retry import retry_feishu_api
from src import get_config

# 配置常量
folder_path = r"D:\monthly\hexi"
history_folder_path = r"D:\monthly\hexi_history"  # 历史文件存储路径
chunk_size = 50000
max_rows_per_sheet = 65000  # 每个工作表的最大行数
file_processing_workers = 4  # 文件处理的线程数

# 定义多个导出任务：每个任务包含 (filter_key, output_filename)
EXPORT_TASKS: List[Tuple[str, str]] = [
    ("赫系官方旗舰店星品", "星品.xlsx"),
    ("赫系官方旗舰店", "旗舰店.xlsx"),
    ("赫系护发精选", "赫系护发精选.xlsx"),
]


def _get_csv_files(folder: str) -> List[str]:
    """
    获取文件夹中的所有CSV文件路径
    :param folder: 文件夹路径
    :return: CSV文件路径列表
    """
    if not os.path.exists(folder):
        raise FileNotFoundError(f"文件夹不存在: {folder}")
    
    csv_files = [
        os.path.join(folder, file)
        for file in os.listdir(folder)
        if file.lower().endswith('.csv') and os.path.isfile(os.path.join(folder, file))
    ]
    return csv_files


def _process_file_multi_filter(file_path: str, filter_keys: Set[str]) -> Dict[str, List[DataFrame]]:
    """
    处理单个文件，一次性为所有filter_key筛选数据，避免重复读取
    优化：只遍历chunk一次，使用groupby高效分组
    :param file_path: 文件路径
    :param filter_keys: 所有需要过滤的关键词集合
    :return: 字典 {filter_key: [DataFrame chunks]}
    """
    result = defaultdict(list)
    file_name = os.path.basename(file_path)
    
    try:
        for chunk in pd.read_csv(file_path, chunksize=chunk_size):
            # 优化：只遍历chunk一次，使用isin快速筛选，然后按filter_key分组
            mask = chunk["达人昵称"].isin(filter_keys)
            if mask.any():  # 如果chunk中有任何匹配的数据
                filtered_chunk = chunk[mask]
                # 使用groupby高效分组，比多次遍历快得多
                grouped = filtered_chunk.groupby("达人昵称")
                for filter_key, group_df in grouped:
                    if filter_key in filter_keys:  # 确保是我们需要的key
                        result[filter_key].append(group_df)
    except Exception as e:
        print(f"读取文件失败 {file_name}: {e}")
        return {key: [] for key in filter_keys}
    
    # 打印统计信息
    for filter_key, chunks in result.items():
        total_rows = sum(len(chunk) for chunk in chunks)
        if total_rows > 0:
            print(f"[{filter_key}] 已读取：{file_name}, 行：{total_rows}")
    
    return dict(result)


def _get_feishu_token() -> str:
    """
    获取飞书tenant_access_token
    :return: token字符串
    """
    app_id = get_config('feishu', 'app_id')
    app_secret = get_config('feishu', 'app_secret')
    data = retry_feishu_api(get_tenant_access_token, [app_id, app_secret])
    if data.get('code') != 0:
        raise Exception(f"获取token失败: {data.get('msg', '未知错误')}")
    return data['tenant_access_token']


def _move_csv_files_to_history() -> None:
    """
    将hexi文件夹中的CSV文件重命名为当前日期并移动到hexi_history文件夹
    """
    try:
        # 确保历史文件夹存在
        if not os.path.exists(history_folder_path):
            os.makedirs(history_folder_path)
            print(f"创建历史文件夹: {history_folder_path}")
        
        # 获取当前日期字符串（格式：YYYYMMDD）
        date_str = datetime.now().strftime("%Y%m%d")
        
        # 获取所有CSV文件
        csv_files = _get_csv_files(folder_path)
        
        if not csv_files:
            print("没有CSV文件需要移动")
            return
        
        moved_count = 0
        for csv_file in csv_files:
            try:
                # 获取原文件名（不含路径）
                original_filename = os.path.basename(csv_file)
                # 获取文件扩展名
                file_ext = os.path.splitext(original_filename)[1]
                # 生成新文件名：日期_原文件名
                new_filename = f"{date_str}_{original_filename}"
                # 目标路径
                dest_path = os.path.join(history_folder_path, new_filename)
                
                # 如果目标文件已存在，添加序号
                counter = 1
                while os.path.exists(dest_path):
                    name_without_ext = os.path.splitext(new_filename)[0]
                    new_filename = f"{name_without_ext}_{counter}{file_ext}"
                    dest_path = os.path.join(history_folder_path, new_filename)
                    counter += 1
                
                # 移动文件
                shutil.move(csv_file, dest_path)
                print(f"已移动文件: {original_filename} -> {new_filename}")
                moved_count += 1
            except Exception as e:
                print(f"移动文件失败 {csv_file}: {e}")
        
        print(f"文件移动完成，共移动 {moved_count} 个文件")
        
    except Exception as e:
        print(f"移动CSV文件到历史文件夹失败: {e}")


def _delete_exported_excel_files() -> None:
    """
    删除导出的Excel文件
    """
    try:
        output_dir = os.path.dirname(folder_path)
        deleted_count = 0
        
        for _, output_filename in EXPORT_TASKS:
            excel_path = os.path.join(output_dir, output_filename)
            if os.path.exists(excel_path):
                try:
                    os.remove(excel_path)
                    print(f"已删除文件: {output_filename}")
                    deleted_count += 1
                except Exception as e:
                    print(f"删除文件失败 {output_filename}: {e}")
        
        print(f"删除Excel文件完成，共删除 {deleted_count} 个文件")
        
    except Exception as e:
        print(f"删除Excel文件失败: {e}")


def _send_file_to_feishu(file_path: str, filter_key: str) -> bool:
    """
    上传文件到飞书并发送到群聊，发送成功后移动CSV文件到历史文件夹
    
    注意：函数内部会捕获所有异常并返回 False，不会向上抛出异常。
    可能遇到的错误情况包括：
    - FileNotFoundError: 文件不存在或配置文件不存在
    - ValueError: 文件为空或超过大小限制（30 MB）
    - TypeError: 参数类型错误
    - Exception: 其他异常（如获取token失败、重试次数过多、网络异常等）
    
    :param file_path: 文件路径
    :param filter_key: 过滤关键词（用于日志）
    :return: 是否成功，失败时返回 False 并打印错误信息
    """
    try:
        # 获取配置
        chat_id = get_config('feishu', 'chat_id')
        if not chat_id:
            print(f"[{filter_key}] 警告: 未配置群聊ID，跳过发送")
            return False
        
        # 获取token
        token = _get_feishu_token()
        
        # 上传文件
        print(f"[{filter_key}] 开始上传文件到飞书: {os.path.basename(file_path)}")
        upload_data = retry_feishu_api(
            upload_file,
            [file_path, token, FileType.XLS]
        )
        
        if upload_data.get('code') != 0:
            print(f"[{filter_key}] 上传文件失败: {upload_data.get('msg', '未知错误')}")
            return False
        
        file_key = upload_data['data']['file_key']
        print(f"[{filter_key}] 文件上传成功，file_key: {file_key}")
        
        # 发送文件消息到群聊
        send_data = retry_feishu_api(
            send_file,
            [chat_id, file_key, token, ReceiveIdType.CHAT_ID.value]
        )
        
        if send_data.get('code') != 0:
            print(f"[{filter_key}] 发送文件消息失败: {send_data.get('msg', '未知错误')}")
            return False
        
        print(f"[{filter_key}] 文件已成功发送到群聊")
        return True
        
    except FileNotFoundError as e:
        print(f"[{filter_key}] 文件不存在: {e}")
        return False
    except Exception as e:
        print(f"[{filter_key}] 发送文件到飞书失败: {e}")
        return False


def split_dataframe_to_sheets(df: DataFrame, max_rows: int) -> Dict[str, DataFrame]:
    """
    将DataFrame分割成多个不超过max_rows的子DataFrame
    :param df: 要分割的DataFrame
    :param max_rows: 每个工作表的最大行数
    :return: 字典 {sheet_name: df}
    """
    if df.empty:
        return {}
    
    total_rows = len(df)
    num_sheets = math.ceil(total_rows / max_rows)
    sheets = {}
    
    for i in range(num_sheets):
        start = i * max_rows
        end = min(start + max_rows, total_rows)
        sheet_name = f"数据_{i + 1}"
        sheets[sheet_name] = df.iloc[start:end].copy()
    
    return sheets


def _merge_and_save(filter_key: str, output_filename: str, all_chunks: List[List[DataFrame]]) -> None:
    """
    合并DataFrame chunks并保存到Excel
    :param filter_key: 过滤关键词
    :param output_filename: 输出文件名
    :param all_chunks: 所有文件的chunks列表 [[chunk1, chunk2], [chunk3, chunk4], ...]
    :return:
    """
    # 合并所有chunks
    chunks_to_concat = []
    for file_chunks in all_chunks:
        if file_chunks:
            chunks_to_concat.extend(file_chunks)
    
    if not chunks_to_concat:
        print(f"[{filter_key}] 警告: 未找到匹配的数据，跳过导出")
        return
    
    final_df = pd.concat(chunks_to_concat, axis=0, ignore_index=True)
    
    # 分割DataFrame到多个工作表
    sheets = split_dataframe_to_sheets(final_df, max_rows_per_sheet)
    if not sheets:
        print(f"[{filter_key}] 警告: 工作表为空，跳过导出")
        return

    # 输出路径
    output_path = os.path.join(os.path.dirname(folder_path), output_filename)

    # 写入Excel文件（多个工作表）
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for sheet_name, sheet_data in sheets.items():
                sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"[{filter_key}] 已写入工作表: {sheet_name}, 行数: {len(sheet_data)}")
        
        print(f"[{filter_key}] 执行完成，文件已保存到: {output_path}，总行数: {len(final_df)}")
        
        # 自动发送文件到飞书群聊
        _send_file_to_feishu(output_path, filter_key)
        
    except Exception as e:
        print(f"[{filter_key}] 写入Excel文件失败: {e}")
        raise


def do_merge_concurrent() -> None:
    """
    并发执行多个导出任务（优化版：只读取一次文件，然后并行处理所有filter_key）
    """
    if not EXPORT_TASKS:
        print("警告: 没有配置导出任务")
        return
    
    # 获取所有需要过滤的关键词
    filter_keys = {filter_key for filter_key, _ in EXPORT_TASKS}
    print(f"开始执行 {len(EXPORT_TASKS)} 个导出任务，涉及 {len(filter_keys)} 个过滤关键词...")
    
    # 获取所有CSV文件路径
    try:
        file_paths = _get_csv_files(folder_path)
        if not file_paths:
            print("警告: 未找到CSV文件")
            return
    except FileNotFoundError as e:
        print(f"错误: {e}")
        return
    
    print(f"找到 {len(file_paths)} 个CSV文件，开始读取...")
    
    # 第一阶段：一次性读取所有文件，同时为所有filter_key过滤数据（只读一次文件！）
    # 使用多线程并行读取文件
    with ThreadPoolExecutor(max_workers=file_processing_workers) as executor:
        file_results = list(executor.map(
            lambda fp: _process_file_multi_filter(fp, filter_keys),
            file_paths
        ))
    
    # 第二阶段：整理数据，为每个filter_key收集所有文件的数据
    filter_data: Dict[str, List[List[DataFrame]]] = defaultdict(list)
    for file_result in file_results:
        for filter_key, chunks in file_result.items():
            if chunks:  # 只添加非空的chunks
                filter_data[filter_key].append(chunks)
    
    print("文件读取完成，开始生成Excel文件...")
    
    # 第三阶段：并发写入Excel文件（写入可以并行进行）
    with ThreadPoolExecutor(max_workers=len(EXPORT_TASKS)) as executor:
        # 提交所有写入任务
        future_to_task = {}
        for filter_key, output_filename in EXPORT_TASKS:
            all_chunks = filter_data.get(filter_key, [])
            future = executor.submit(_merge_and_save, filter_key, output_filename, all_chunks)
            future_to_task[future] = (filter_key, output_filename)
        
        # 等待所有任务完成
        completed_count = 0
        failed_count = 0
        
        for future in as_completed(future_to_task):
            filter_key, output_filename = future_to_task[future]
            try:
                future.result()  # 获取结果，如果有异常会在这里抛出
                completed_count += 1
                print(f"[{filter_key}] 任务完成")
            except Exception as exc:
                failed_count += 1
                print(f"[{filter_key}] 任务发生异常: {exc}")
    
    print(f"所有导出任务已完成！成功: {completed_count}, 失败: {failed_count}")
    
    # 第四阶段：文件管理
    # 只有当所有任务都成功完成时，才移动CSV文件和删除Excel文件
    if failed_count == 0 and completed_count > 0:
        print("\n开始文件管理...")
        # 移动CSV文件到历史文件夹
        _move_csv_files_to_history()
        # 删除导出的Excel文件
        _delete_exported_excel_files()
        print("文件管理完成")
    else:
        print(f"\n由于有任务失败（成功: {completed_count}, 失败: {failed_count}），跳过文件管理操作")


if __name__ == '__main__':
    # 并发执行所有导出任务
    do_merge_concurrent()