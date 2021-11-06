import os

'''遍历指定文件目录，返回列表（该目录下所有文件名称）'''


def traverse_files(file_dir):
    files_global = []
    for files in os.listdir(file_dir):
        files_global.append(files)
    return files_global
