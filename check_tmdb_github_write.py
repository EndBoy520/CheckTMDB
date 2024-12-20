import requests
from time import sleep
import random
import time
import os
import platform
import sys
from datetime import datetime, timezone, timedelta
from retry import retry
import socket

DOMAINS = [
    'themoviedb.org',
    'www.themoviedb.org',
    'auth.themoviedb.org',
    'api.themoviedb.org',
    'tmdb.org',
    'api.tmdb.org',
    'image.tmdb.org',
    'thetvdb.com',
    'api.thetvdb.com'
]

Tmdb_Host_TEMPLATE = """# Tmdb Hosts Start
{content}
# Update time: {update_time}
# IPv4 Update url: https://github.com/cnwikee/CheckTMDB/blob/main/Tmdb_host_ipv4
# IPv6 Update url: https://github.com/cnwikee/CheckTMDB/blob/main/Tmdb_host_ipv6
# Star me: https://github.com/cnwikee/CheckTMDB
# Tmdb Hosts End\n"""

def write_file(ipv4_hosts_content: str, ipv6_hosts_content: str, update_time: str) -> bool:
    output_doc_file_path = os.path.join(os.path.dirname(__file__), "README.md")
    template_path = os.path.join(os.path.dirname(__file__), "README_template.md")
    
    if os.path.exists(output_doc_file_path):
        with open(output_doc_file_path, "r", encoding='utf-8') as old_readme_md:
            old_readme_md_content = old_readme_md.read()            
            if old_readme_md_content:
                old_ipv4_block = old_readme_md_content.split("```bash")[1].split("```")[0].strip()
                old_ipv4_hosts = old_ipv4_block.split("# Update time:")[0].strip()

                old_ipv6_block = old_readme_md_content.split("```bash")[2].split("```")[0].strip()
                old_ipv6_hosts = old_ipv6_block.split("# Update time:")[0].strip()
                
                if ipv4_hosts_content != "":
                    new_ipv4_hosts = ipv4_hosts_content.split("# Update time:")[0].strip()
                    if old_ipv4_hosts == new_ipv4_hosts:
                        print("ipv4 host not change")
                        w_ipv4_block = old_ipv4_block
                    else:
                        w_ipv4_block = ipv4_hosts_content
                        write_host_file(ipv4_hosts_content, 'ipv4')
                else:
                    print("ipv4_hosts_content is null")
                    w_ipv4_block = old_ipv4_block

                if ipv6_hosts_content != "":
                    new_ipv6_hosts = ipv6_hosts_content.split("# Update time:")[0].strip()
                    if old_ipv6_hosts == new_ipv6_hosts:
                        print("ipv6 host not change")
                        w_ipv6_block = old_ipv6_block
                    else:
                        w_ipv6_block = ipv6_hosts_content
                        write_host_file(ipv6_hosts_content, 'ipv6')
                else:
                    print("ipv6_hosts_content is null")
                    w_ipv6_block = old_ipv6_block
                
                with open(template_path, "r", encoding='utf-8') as temp_fb:
                    template_str = temp_fb.read()
                    hosts_content = template_str.format(ipv4_hosts_str=w_ipv4_block, ipv6_hosts_str=w_ipv6_block, update_time=update_time)

                    with open(output_doc_file_path, "w", encoding='utf-8') as output_fb:
                        output_fb.write(hosts_content)
                return True
        return False
               
                

def write_host_file(hosts_content: str, filename: str) -> None:
    output_file_path = os.path.join(os.path.dirname(__file__), "Tmdb_host_" + filename)
    if len(sys.argv) >= 2 and sys.argv[1].upper() == '-G':
        print("\n~追加Github ip~")
        hosts_content = hosts_content + "\n" + (get_github_hosts() or "")
    with open(output_file_path, "w", encoding='utf-8') as output_fb:
        output_fb.write(hosts_content)
        print("\n~最新TMDB" + filename + "地址已更新~")

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


def get_github_hosts() -> None:
    github_hosts_urls = [
        "https://hosts.gitcdn.top/hosts.txt",
        "https://raw.githubusercontent.com/521xueweihan/GitHub520/refs/heads/main/hosts",
        "https://gitlab.com/ineo6/hosts/-/raw/master/next-hosts",
        "https://raw.githubusercontent.com/ittuann/GitHub-IP-hosts/refs/heads/main/hosts_single"
    ]
    all_failed = True
    for url in github_hosts_urls:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                github_hosts = response.text
                all_failed = False
                break
            else:
                print(f"\n从 {url} 获取GitHub hosts失败: HTTP {response.status_code}")
        except Exception as e:
            print(f"\n从 {url} 获取GitHub hosts时发生错误: {str(e)}")
    if all_failed:
        print("\n获取GitHub hosts失败: 所有Url项目失败！")
        return
    else:
        return github_hosts

def is_ci_environment():
    ci_environment_vars = {
        'GITHUB_ACTIONS': 'true',
        'TRAVIS': 'true',
        'CIRCLECI': 'true'
    }
    for env_var, expected_value in ci_environment_vars.items():
        env_value = os.getenv(env_var)
        if env_value is not None and str(env_value).lower() == expected_value.lower():
            return True
    return False
    

@retry(tries=3)
def get_csrf_token(udp):
    """获取CSRF Token"""
    try:
        url = f'https://dnschecker.org/ajax_files/gen_csrf.php?udp={udp}'
        headers = {
            'referer': 'https://dnschecker.org/country/cn/','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            csrf = response.json().get('csrf')
            print(f"获取到的CSRF Token: {csrf}")
            return csrf
        else:
            print(f"获取CSRF Token失败，HTTP状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"获取CSRF Token时发生错误: {str(e)}")
        return None

@retry(tries=3)
def get_domain_ips(domain, csrf_token, udp, argument):
    url = f'https://dnschecker.org/ajax_files/api/363/{argument}/{domain}?dns_key=country&dns_value=cn&v=0.36&cd_flag=1&upd={udp}'
    headers = {'csrftoken': csrf_token, 'referer':'https://dnschecker.org/country/cn/','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'result' in data and 'ips' in data['result']:
                ips_str = data['result']['ips']
                if '<br />' in ips_str:
                    return [ip.strip() for ip in ips_str.split('<br />') if ip.strip()]
                else:
                    return [ips_str.strip()] if ips_str.strip() else []
            else:
                print(f"获取 {domain} 的IP列表失败：返回数据格式不正确")
                return []
        else:
            print(f"获取 {domain} 的IP列表失败，HTTP状态码: {response.status_code}")
            return []
    except Exception as e:
        print(f"获取 {domain} 的IP列表时发生错误: {str(e)}")
        return []

def ping_ip(ip, port=80):
    print(f"使用TCP连接测试IP地址的延迟（毫秒）")
    try:
        print(f"\n开始 ping {ip}...")
        start_time = time.time()
        with socket.create_connection((ip, port), timeout=2) as sock:
            latency = (time.time() - start_time) * 1000  # 转换为毫秒
            print(f"IP: {ip} 的平均延迟: {latency}ms")
            return latency
    except Exception as e:
        print(f"Ping {ip} 时发生错误: {str(e)}")
        return float('inf')
    
def find_fastest_ip(ips):
    """找出延迟最低的IP地址"""
    if not ips:
        return None
    
    fastest_ip = None
    min_latency = float('inf')
    ip_latencies = []  # 存储所有IP及其延迟
    
    for ip in ips:
        ip = ip.strip()
        if not ip:
            continue
            
        print(f"正在测试 IP: {ip}")
        latency = ping_ip(ip)
        ip_latencies.append((ip, latency))
        print(f"IP: {ip} 延迟: {latency}ms")
        
        if latency < min_latency:
            min_latency = latency
            fastest_ip = ip
            
        sleep(0.5) 
    
    print("\n所有IP延迟情况:")
    for ip, latency in ip_latencies:
        print(f"IP: {ip} - 延迟: {latency}ms")
    
    if fastest_ip:
        print(f"\n最快的IP是: {fastest_ip}，延迟: {min_latency}ms")
    
    return fastest_ip

def main():
    print("开始检测TMDB相关域名的最快IP...")
    udp = random.random() * 1000 + (int(time.time() * 1000) % 1000)
    # 获取CSRF Token
    csrf_token = get_csrf_token(udp)
    if not csrf_token:
        print("无法获取CSRF Token，程序退出")
        sys.exit(1)

    ipv4_ips, ipv6_ips, ipv4_results, ipv6_results = [], [], [], []

    for domain in DOMAINS:
        print(f"\n正在处理域名: {domain}")       
        ipv4_ips = get_domain_ips(domain, csrf_token, udp, "A")
        ipv6_ips = get_domain_ips(domain, csrf_token, udp, "AAAA")

        if not ipv4_ips and not ipv6_ips:
            print(f"无法获取 {domain} 的IP列表，跳过该域名")
            continue
        
        # 处理 IPv4 地址
        if ipv4_ips:
            fastest_ipv4 = find_fastest_ip(ipv4_ips)
            if fastest_ipv4:
                ipv4_results.append([fastest_ipv4, domain])
                print(f"域名 {domain} 的最快IPv4是: {fastest_ipv4}")
            else:
                ipv4_results.append([ipv4_ips[0], domain])
        
        # 处理 IPv6 地址
        if ipv6_ips:
            fastest_ipv6 = find_fastest_ip(ipv6_ips)
            if fastest_ipv6:
                ipv6_results.append([fastest_ipv6, domain])
                print(f"域名 {domain} 的最快IPv6是: {fastest_ipv6}")
            else:
                # 兜底：可能存在无法正确获取 fastest_ipv6 的情况，则将第一个IP赋值
                ipv6_results.append([ipv6_ips[0], domain])
        
        sleep(1)  # 避免请求过于频繁
    
    # 保存结果到文件
    if not ipv4_results and not ipv6_results:
        print(f"程序出错：未获取任何domain及对应IP，请检查接口~")
        sys.exit(1)

    # 生成更新时间
    update_time = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
    
    ipv4_hosts_content = Tmdb_Host_TEMPLATE.format(content="\n".join(f"{ip:<27} {domain}" for ip, domain in ipv4_results), update_time=update_time) if ipv4_results else ""
    ipv6_hosts_content = Tmdb_Host_TEMPLATE.format(content="\n".join(f"{ip:<50} {domain}" for ip, domain in ipv6_results), update_time=update_time) if ipv6_results else ""

    write_file(ipv4_hosts_content, ipv6_hosts_content, update_time)
    
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
