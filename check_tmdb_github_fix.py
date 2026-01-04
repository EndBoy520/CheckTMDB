import requests
from time import sleep
import random
import time
import os
import sys
from datetime import datetime, timezone, timedelta
from retry import retry
import socket

country_code = 'jp' #节点

DOMAINS = [
    'tmdb.org',
    'api.tmdb.org',
    'files.tmdb.org',
    'themoviedb.org',
    'api.themoviedb.org',
    'www.themoviedb.org',
    'auth.themoviedb.org',
    'image.tmdb.org',
    'images.tmdb.org',
    'imdb.com',
    'www.imdb.com',
    'secure.imdb.com',
    's.media-imdb.com',
    'us.dd.imdb.com',
    'www.imdb.to',
    'origin-www.imdb.com',
    'ia.media-imdb.com',
    'thetvdb.com',
    'api.thetvdb.com',
    'ia.media-imdb.com',
    'f.media-amazon.com',
    'imdb-video.media-imdb.com'
]

Tmdb_Host_TEMPLATE = """# Tmdb Hosts Start
{content}
# Update time: {update_time}
# IPv4 Update url: https://raw.githubusercontent.com/cnwikee/CheckTMDB/refs/heads/main/Tmdb_host_ipv4
# IPv6 Update url: https://raw.githubusercontent.com/cnwikee/CheckTMDB/refs/heads/main/Tmdb_host_ipv6
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
def get_domain_ips(domain, csrf_token=None, udp=None, argument="A"):
    """直接使用socket.getaddrinfo获取域名IP，支持IPv4和IPv6"""
    try:
        ips = []
        family = socket.AF_INET if argument == "A" else socket.AF_INET6
        
        # 获取域名的IP地址列表
        addrinfo_list = socket.getaddrinfo(domain, 80, family, socket.SOCK_STREAM)
        
        # 提取唯一的IP地址
        seen_ips = set()
        for addrinfo in addrinfo_list:
            ip = addrinfo[4][0]
            if ip not in seen_ips:
                seen_ips.add(ip)
                ips.append(ip)
        
        print(f"直接解析域名 {domain} 获取到 {argument} 记录IP: {ips}")
        return ips
    except Exception as e:
        print(f"解析域名 {domain} 时发生错误: {str(e)}")
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

    ipv4_ips, ipv6_ips, ipv4_results, ipv6_results = [], [], [], []

    for domain in DOMAINS:
        print(f"\n正在处理域名: {domain}")       
        ipv4_ips = get_domain_ips(domain, argument="A")
        ipv6_ips = get_domain_ips(domain, argument="AAAA")

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
        
        sleep(0.5)  # 减少等待时间
    
    # 保存结果到文件
    if not ipv4_results and not ipv6_results:
        print(f"程序出错：未获取任何domain及对应IP，请检查网络连接~")
        sys.exit(1)

    # 生成更新时间
    update_time = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
    
    ipv4_hosts_content = Tmdb_Host_TEMPLATE.format(content="\n".join(f"{ip:<27} {domain}" for ip, domain in ipv4_results), update_time=update_time) if ipv4_results else ""
    ipv6_hosts_content = Tmdb_Host_TEMPLATE.format(content="\n".join(f"{ip:<50} {domain}" for ip, domain in ipv6_results), update_time=update_time) if ipv6_results else ""

    write_file(ipv4_hosts_content, ipv6_hosts_content, update_time)


if __name__ == "__main__":
    main()
