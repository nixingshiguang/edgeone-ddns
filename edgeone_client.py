#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于官方SDK的EdgeOne客户端 - 最稳定可靠的实现
"""

import json
import logging
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.teo.v20220901 import teo_client, models

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EdgeOneClient:
    """基于官方SDK的EdgeOne客户端"""
    
    def __init__(self, secret_id: str, secret_key: str, region: str = "ap-shanghai"):
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.region = region
        self.version = "2022-09-01"
        self.endpoint = "teo.tencentcloudapi.com"
        
        # 创建SDK客户端
        self.client = self._create_client()
    
    def _create_client(self):
        """创建SDK客户端"""
        try:
            # 实例化一个认证对象
            cred = credential.Credential(self.secret_id, self.secret_key)
            
            # 实例化一个http选项
            httpProfile = HttpProfile()
            httpProfile.endpoint = self.endpoint
            
            # 实例化一个client选项
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            
            # 实例化要请求产品的client对象
            client = teo_client.TeoClient(cred, "", clientProfile)
            
            logging.info("✅ EdgeOne SDK客户端创建成功")
            return client
            
        except Exception as e:
            logging.error(f"❌ 创建EdgeOne SDK客户端失败: {e}")
            raise
    
    def describe_dns_records(self, zone_id: str, filters: list = None, limit: int = 1000, offset: int = 0) -> dict:
        """查询DNS记录"""
        try:
            req = models.DescribeDnsRecordsRequest()
            params = {
                "ZoneId": zone_id,
                "Limit": limit,
                "Offset": offset
            }
            
            if filters:
                params["Filters"] = filters
            
            req.from_json_string(json.dumps(params))
            resp = self.client.DescribeDnsRecords(req)
            
            # 解析响应
            response_data = json.loads(resp.to_json_string())
            logging.info(f"✅ 查询DNS记录成功，找到 {response_data.get('TotalCount', 0)} 条记录")
            
            return response_data
            
        except Exception as e:
            logging.error(f"❌ 查询DNS记录失败: {e}")
            raise
    
    def create_dns_record(self, zone_id: str, name: str, record_type: str, 
                         content: str, ttl: int = 300, location: str = "Default") -> dict:
        """创建DNS记录"""
        try:
            req = models.CreateDnsRecordRequest()
            params = {
                "ZoneId": zone_id,
                "Name": name,
                "Type": record_type,
                "Content": content,
                "TTL": ttl,
                "Location": location
            }
            
            req.from_json_string(json.dumps(params))
            resp = self.client.CreateDnsRecord(req)
            
            # 解析响应
            response_data = json.loads(resp.to_json_string())
            logging.info(f"✅ 创建DNS记录成功: {name} -> {content}")
            
            return response_data
            
        except Exception as e:
            logging.error(f"❌ 创建DNS记录失败: {e}")
            raise
    
    def modify_dns_record(self, zone_id: str, record_id: str, name: str, 
                         record_type: str, content: str, ttl: int = 300, 
                         location: str = "Default") -> dict:
        """修改DNS记录 - 使用批量修改接口"""
        try:
            req = models.ModifyDnsRecordsRequest()
            params = {
                "ZoneId": zone_id,
                "DnsRecords": [
                    {
                        "RecordId": record_id,
                        "Name": name,
                        "Type": record_type,
                        "Content": content,
                        "Ttl": ttl
                    }
                ]
            }
            
            req.from_json_string(json.dumps(params))
            resp = self.client.ModifyDnsRecords(req)
            
            # 解析响应
            response_data = json.loads(resp.to_json_string())
            logging.info(f"✅ 修改DNS记录成功: {name} -> {content}")
            
            return response_data
            
        except Exception as e:
            logging.error(f"❌ 修改DNS记录失败: {e}")
            raise
    
    def delete_dns_record(self, zone_id: str, record_id: str) -> dict:
        """删除DNS记录"""
        try:
            req = models.DeleteDnsRecordRequest()
            params = {
                "ZoneId": zone_id,
                "RecordId": record_id
            }
            
            req.from_json_string(json.dumps(params))
            resp = self.client.DeleteDnsRecord(req)
            
            # 解析响应
            response_data = json.loads(resp.to_json_string())
            logging.info(f"✅ 删除DNS记录成功: {record_id}")
            
            return response_data
            
        except Exception as e:
            logging.error(f"❌ 删除DNS记录失败: {e}")
            raise
    
    def find_a_record(self, zone_id: str, domain: str) -> dict:
        """查找指定域名的A记录"""
        try:
            filters = [
                {
                    "Name": "name",
                    "Values": [domain],
                    "Fuzzy": False
                },
                {
                    "Name": "type",
                    "Values": ["A"],
                    "Fuzzy": False
                }
            ]
            
            response = self.describe_dns_records(zone_id, filters)
            
            dns_records = response.get("DnsRecords", [])
            for record in dns_records:
                if record["Name"] == domain and record["Type"] == "A":
                    logging.info(f"✅ 找到A记录: {domain} -> {record['Content']}")
                    return record
            
            logging.info(f"⚠️ 未找到域名 {domain} 的A记录")
            return None
            
        except Exception as e:
            logging.error(f"❌ 查找A记录失败 {domain}: {e}")
            return None
    
    def find_aaaa_record(self, zone_id: str, domain: str) -> dict:
        """查找指定域名的AAAA记录"""
        try:
            filters = [
                {
                    "Name": "name",
                    "Values": [domain],
                    "Fuzzy": False
                },
                {
                    "Name": "type",
                    "Values": ["AAAA"],
                    "Fuzzy": False
                }
            ]
            
            response = self.describe_dns_records(zone_id, filters)
            
            dns_records = response.get("DnsRecords", [])
            for record in dns_records:
                if record["Name"] == domain and record["Type"] == "AAAA":
                    logging.info(f"✅ 找到AAAA记录: {domain} -> {record['Content']}")
                    return record
            
            logging.info(f"⚠️ 未找到域名 {domain} 的AAAA记录")
            return None
            
        except Exception as e:
            logging.error(f"❌ 查找AAAA记录失败 {domain}: {e}")
            return None
    
    def update_or_create_a_record(self, zone_id: str, domain: str, ip_address: str) -> dict:
        """更新或创建A记录"""
        result = {
            "action": "none",
            "success": False,
            "message": "",
            "record_id": None
        }
        
        try:
            # 查找现有记录
            existing_record = self.find_a_record(zone_id, domain)
            
            if existing_record:
                # 检查IP是否需要更新
                if existing_record["Content"] == ip_address:
                    result.update({
                        "action": "no_change",
                        "success": True,
                        "message": f"域名 {domain} 的A记录IP已是 {ip_address}，无需更新",
                        "record_id": existing_record["RecordId"]
                    })
                    logging.info(result["message"])
                else:
                    # 更新现有记录
                    response = self.modify_dns_record(
                        zone_id, 
                        existing_record["RecordId"],
                        domain,
                        "A",
                        ip_address,
                        existing_record.get("TTL", 300),
                        existing_record.get("Location", "Default")
                    )
                    
                    result.update({
                        "action": "updated",
                        "success": True,
                        "message": f"域名 {domain} 的A记录已更新为 {ip_address}",
                        "record_id": existing_record["RecordId"],
                        "old_ip": existing_record["Content"],
                        "new_ip": ip_address
                    })
                    logging.info(result["message"])
            else:
                # 创建新记录
                response = self.create_dns_record(zone_id, domain, "A", ip_address)
                
                if "RecordId" in response:
                    result.update({
                        "action": "created",
                        "success": True,
                        "message": f"域名 {domain} 的A记录已创建为 {ip_address}",
                        "record_id": response["RecordId"],
                        "new_ip": ip_address
                    })
                    logging.info(result["message"])
                else:
                    raise Exception("创建DNS记录失败，未返回DnsRecordId")
            
        except Exception as e:
            result.update({
                "success": False,
                "message": f"操作域名 {domain} 失败: {str(e)}"
            })
            logging.error(result["message"])
        
        return result
    
    def update_or_create_aaaa_record(self, zone_id: str, domain: str, ipv6_address: str) -> dict:
        """更新或创建AAAA记录"""
        result = {
            "action": "none",
            "success": False,
            "message": "",
            "record_id": None
        }
        
        try:
            # 查找现有记录
            existing_record = self.find_aaaa_record(zone_id, domain)
            
            if existing_record:
                # 检查IPv6是否需要更新
                if existing_record["Content"] == ipv6_address:
                    result.update({
                        "action": "no_change",
                        "success": True,
                        "message": f"域名 {domain} 的AAAA记录IP已是 {ipv6_address}，无需更新",
                        "record_id": existing_record["RecordId"]
                    })
                    logging.info(result["message"])
                else:
                    # 更新现有记录
                    response = self.modify_dns_record(
                        zone_id, 
                        existing_record["RecordId"],
                        domain,
                        "AAAA",
                        ipv6_address,
                        existing_record.get("TTL", 300),
                        existing_record.get("Location", "Default")
                    )
                    
                    result.update({
                        "action": "updated",
                        "success": True,
                        "message": f"域名 {domain} 的AAAA记录已更新为 {ipv6_address}",
                        "record_id": existing_record["RecordId"],
                        "old_ip": existing_record["Content"],
                        "new_ip": ipv6_address
                    })
                    logging.info(result["message"])
            else:
                # 创建新记录
                response = self.create_dns_record(zone_id, domain, "AAAA", ipv6_address)
                
                if "RecordId" in response:
                    result.update({
                        "action": "created",
                        "success": True,
                        "message": f"域名 {domain} 的AAAA记录已创建为 {ipv6_address}",
                        "record_id": response["RecordId"],
                        "new_ip": ipv6_address
                    })
                    logging.info(result["message"])
                else:
                    raise Exception("创建DNS记录失败，未返回DnsRecordId")
            
        except Exception as e:
            result.update({
                "success": False,
                "message": f"操作域名 {domain} 失败: {str(e)}"
            })
            logging.error(result["message"])
        
        return result

def test_sdk_client():
    """测试基于SDK的客户端"""
    print("🔧 测试基于官方SDK的EdgeOne客户端...")
    
    # 读取配置
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            secret_id = config.get('secret_id', '')
            secret_key = config.get('secret_key', '')
            zone_id = config.get('zone_id', '')
    except Exception as e:
        print(f"❌ 读取配置失败: {e}")
        return False
    
    if not secret_id or not secret_key:
        print("❌ 密钥未配置")
        return False
    
    # 创建SDK客户端
    try:
        client = SDKEdgeOneClient(secret_id, secret_key)
        print("✅ SDK客户端创建成功")
    except Exception as e:
        print(f"❌ SDK客户端创建失败: {e}")
        return False
    
    # 测试查询DNS记录
    if zone_id:
        print(f"\n🧪 测试查询DNS记录...")
        try:
            response = client.describe_dns_records(zone_id, limit=5)
            print("✅ 查询DNS记录成功!")
            
            dns_records = response.get("DnsRecords", [])
            print(f"找到 {len(dns_records)} 条DNS记录")
            
            if dns_records:
                print("前3条记录:")
                for i, record in enumerate(dns_records[:3]):
                    print(f"  {i+1}. {record['Name']} ({record['Type']}) -> {record['Content']}")
            
            return True
            
        except Exception as e:
            print(f"❌ 查询DNS记录失败: {e}")
            return False
    else:
        print("⚠️ Zone ID未配置，跳过测试")
        return True

if __name__ == "__main__":
    success = test_sdk_client()
    if success:
        print("\n🎉 基于官方SDK的客户端测试成功!")
        print("💡 这是生产环境推荐使用的实现方式")
    exit(0 if success else 1)