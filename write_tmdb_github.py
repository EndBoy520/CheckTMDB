import os
import platform
import datetime

def read_tmdb_host(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def write_to_system_hosts(ipv4_content, ipv6_content):
    windows_hosts_path = "C:\\Windows\\System32\\drivers\\etc\\hosts"
    linux_hosts_path = "/etc/hosts"
    
    # 根据操作系统选择 hosts 文件路径
    if platform.system().lower() == "windows":
        hosts_path = windows_hosts_path
    else:
        hosts_path = linux_hosts_path
    
    # 读取现有的 hosts 文件内容
    with open(hosts_path, "r", encoding="utf-8") as file:
        original_content = file.read()
    
    # 标记开始和结束
    start_marker = "### Tmdb Hosts Start ###"
    end_marker = "### Tmdb Hosts End ###"
    
    # 查找标记位置
    start_index = original_content.find(start_marker)
    end_index = original_content.find(end_marker)
    
    # 如果标记存在，替换中间内容；否则，添加新内容
    if start_index != -1 and end_index != -1:
        new_content = (original_content[:start_index + len(start_marker)] + "\n" +
                       ipv4_content + "\n" +
                       ipv6_content + "\n" +
                       original_content[end_index:])
    else:
        new_content = (original_content.strip() + "\n" +
                       start_marker + "\n" +
                       ipv4_content + "\n" +
                       ipv6_content + "\n" +
                       end_marker + "\n")
    
    # 写入更新后的内容到 hosts 文件
    with open(hosts_path, "w", encoding="utf-8") as file:
        file.write(new_content)

def main():
    # 假设 Tmdb_host_ipv4 和 Tmdb_host_ipv6 文件路径
    tmdb_host_ipv4_path = output_doc_file_path = os.path.join(os.path.dirname(__file__), "Tmdb_host_ipv4")
    tmdb_host_ipv6_path = output_doc_file_path = os.path.join(os.path.dirname(__file__), "Tmdb_host_ipv6")
    
    # 读取 Tmdb_host_ipv4 和 Tmdb_host_ipv6 内容
    ipv4_content = read_tmdb_host(tmdb_host_ipv4_path)
    ipv6_content = read_tmdb_host(tmdb_host_ipv6_path)
    
    # 写入系统 hosts 文件
    write_to_system_hosts(ipv4_content, ipv6_content)

if __name__ == "__main__":
    main()