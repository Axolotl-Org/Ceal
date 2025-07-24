#!/usr/bin/env python

from get_para import get_config_from_web

mapper, resolv = get_config_from_web()


if __name__ == '__main__':
    
    host_rules = ""
    resolv_rules = ""
    
    for fake, v in mapper.items():
        for real in v:
            host_rules.join(f"MAP {real} {fake},")
    
    for ip, v in mapper.items():
        for domain in v:
            resolv_rules.join(f"MAP {domain} {ip},")
    
    print(f'--host_rules="{host_rules}"', f'--host-resolver-rules="{resolv_rules}')
