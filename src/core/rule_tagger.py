import re
from typing import List, Dict, Any, Optional, Set
from ..models.tags import (
    Tag, ContentType, Domain, Priority, Stakeholder
)


class RuleTagger:
    """Rule-based tagger for construction meeting content"""
    
    def __init__(self):
        self._init_patterns()
    
    def _init_patterns(self):
        """Initialize regex patterns for different tag types"""
        
        # Content type patterns
        self.content_patterns = {
            ContentType.DECISION: [
                r"決定(?:事項|した|します)",
                r"(?:に|と)決め(?:ました|る)",
                r"確定(?:した|します)",
                r"承認(?:され|し)ました",
                r"合意(?:に達|し)ました"
            ],
            ContentType.ISSUE: [
                r"課題(?:が|は|として)",
                r"問題(?:が|は|点)",
                r"懸念(?:事項|が)",
                r"リスク(?:が|は)",
                r"未解決",
                r"検討(?:が必要|事項)"
            ],
            ContentType.ACTION_ITEM: [
                r"(?:まで|までに)(?:実施|完了|提出)",
                r"アクション(?:アイテム|項目)",
                r"タスク(?:として|は)",
                r"宿題(?:事項|として)",
                r"(?:を|は)(?:担当|対応)(?:する|します)",
                r"次回(?:まで|までに)"
            ],
            ContentType.INFORMATION: [
                r"(?:情報|資料)(?:共有|提供)",
                r"(?:お知らせ|連絡)(?:事項|です)",
                r"報告(?:事項|します)",
                r"説明(?:します|いたします)"
            ],
            ContentType.DISCUSSION: [
                r"議論(?:が必要|します|の結果)",
                r"意見(?:交換|を)",
                r"検討(?:します|中)",
                r"協議(?:事項|します)"
            ]
        }
        
        # Domain patterns
        self.domain_patterns = {
            Domain.STRUCTURE: [
                r"(?:鉄筋|RC|S造|構造)",
                r"(?:基礎|躯体|梁|柱|スラブ)",
                r"(?:耐震|制震|免震)",
                r"構造(?:計算|設計|図)"
            ],
            Domain.EQUIPMENT: [
                r"(?:設備|電気|空調|衛生)",
                r"(?:配管|配線|ダクト)",
                r"(?:給排水|換気|照明)",
                r"設備(?:図|機器)"
            ],
            Domain.CONSTRUCTION_MANAGEMENT: [
                r"(?:施工|工事|現場)",
                r"(?:工程|進捗|管理)",
                r"(?:施工図|計画書)",
                r"現場(?:監督|管理)"
            ],
            Domain.DESIGN: [
                r"(?:設計|図面|詳細図)",
                r"(?:意匠|デザイン)",
                r"(?:仕様|仕上げ)",
                r"設計(?:変更|図書)"
            ],
            Domain.SAFETY: [
                r"(?:安全|労災|事故)",
                r"(?:危険|ヒヤリハット)",
                r"(?:安全対策|防護)",
                r"安全(?:管理|教育|パトロール)"
            ],
            Domain.QUALITY: [
                r"(?:品質|検査|試験)",
                r"(?:不良|手直し|是正)",
                r"(?:品質管理|QC)",
                r"検査(?:結果|報告)"
            ],
            Domain.COST: [
                r"(?:コスト|費用|予算)",
                r"(?:見積|金額|単価)",
                r"(?:追加工事|変更)",
                r"予算(?:管理|超過)"
            ],
            Domain.SCHEDULE: [
                r"(?:工程|スケジュール|日程)",
                r"(?:遅延|前倒し|調整)",
                r"(?:マイルストーン|期限)",
                r"工程(?:表|管理|会議)"
            ]
        }
        
        # Priority patterns
        self.priority_patterns = {
            Priority.HIGH: [
                r"(?:至急|緊急|即座)",
                r"(?:最優先|重要|critical)",
                r"(?:今すぐ|直ちに)",
                r"(?:期限厳守|必須)"
            ],
            Priority.MEDIUM: [
                r"(?:通常|標準|normal)",
                r"(?:今週中|今月中)",
                r"(?:できるだけ早く|なるべく)"
            ],
            Priority.LOW: [
                r"(?:後回し|余裕がある時)",
                r"(?:急がない|ゆっくり)",
                r"(?:参考|FYI)"
            ]
        }
        
        # Stakeholder patterns
        self.stakeholder_patterns = {
            Stakeholder.CLIENT: [
                r"(?:発注者|施主|オーナー)",
                r"(?:クライアント|顧客)",
                r"(?:事業主|建築主)"
            ],
            Stakeholder.DESIGNER: [
                r"(?:設計者|設計事務所)",
                r"(?:建築家|デザイナー)",
                r"(?:設計士|意匠設計)"
            ],
            Stakeholder.CONTRACTOR: [
                r"(?:施工者|ゼネコン|建設会社)",
                r"(?:元請|工事業者)",
                r"(?:施工会社|建築会社)"
            ],
            Stakeholder.SUPERVISOR: [
                r"(?:監理者|工事監理)",
                r"(?:監督員|現場監督)",
                r"(?:管理者|監理事務所)"
            ],
            Stakeholder.SUBCONTRACTOR: [
                r"(?:協力業者|下請け|専門工事)",
                r"(?:サブコン|専門業者)",
                r"(?:職人|作業員)"
            ]
        }
        
        # Compile all patterns
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for better performance"""
        self.compiled_patterns = {}
        
        for category, patterns_dict in [
            ("content_type", self.content_patterns),
            ("domain", self.domain_patterns),
            ("priority", self.priority_patterns),
            ("stakeholder", self.stakeholder_patterns)
        ]:
            self.compiled_patterns[category] = {}
            for key, patterns in patterns_dict.items():
                combined_pattern = "|".join(f"({p})" for p in patterns)
                self.compiled_patterns[category][key] = re.compile(
                    combined_pattern, re.IGNORECASE
                )
    
    def tag_content(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Apply rule-based tagging to text content"""
        tags = {
            "content_type": None,
            "domains": [],
            "priority": None,
            "stakeholders": [],
            "custom_tags": []
        }
        
        # Detect content type
        content_type_scores = {}
        for content_type, pattern in self.compiled_patterns["content_type"].items():
            matches = pattern.findall(text)
            if matches:
                content_type_scores[content_type] = len(matches)
        
        if content_type_scores:
            tags["content_type"] = max(content_type_scores, key=content_type_scores.get)
        
        # Detect domains
        domains_found = set()
        for domain, pattern in self.compiled_patterns["domain"].items():
            if pattern.search(text):
                domains_found.add(domain)
        tags["domains"] = list(domains_found)
        
        # Detect priority
        for priority, pattern in self.compiled_patterns["priority"].items():
            if pattern.search(text):
                tags["priority"] = priority
                break
        
        # Detect stakeholders
        stakeholders_found = set()
        for stakeholder, pattern in self.compiled_patterns["stakeholder"].items():
            if pattern.search(text):
                stakeholders_found.add(stakeholder)
        tags["stakeholders"] = list(stakeholders_found)
        
        # Add custom tags based on specific keywords
        custom_tags = self._extract_custom_tags(text)
        tags["custom_tags"] = custom_tags
        
        return tags
    
    def _extract_custom_tags(self, text: str) -> List[Tag]:
        """Extract custom tags based on specific patterns"""
        custom_tags = []
        
        # Extract dates
        date_pattern = re.compile(r"\d{1,2}[月/]\d{1,2}[日]?")
        dates = date_pattern.findall(text)
        for date in dates:
            custom_tags.append(Tag(
                category="date",
                value=date,
                confidence=1.0,
                source="rule"
            ))
        
        # Extract monetary amounts
        money_pattern = re.compile(r"(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:円|万円|億円)")
        amounts = money_pattern.findall(text)
        for amount in amounts:
            custom_tags.append(Tag(
                category="amount",
                value=amount,
                confidence=1.0,
                source="rule"
            ))
        
        # Extract percentages
        percent_pattern = re.compile(r"(\d+(?:\.\d+)?)\s*[%％]")
        percentages = percent_pattern.findall(text)
        for percentage in percentages:
            custom_tags.append(Tag(
                category="percentage",
                value=f"{percentage}%",
                confidence=1.0,
                source="rule"
            ))
        
        # Extract room/area names
        room_pattern = re.compile(r"(?:会議室|事務所|現場|工場|倉庫|[\d]+階)")
        rooms = room_pattern.findall(text)
        for room in rooms:
            custom_tags.append(Tag(
                category="location",
                value=room,
                confidence=1.0,
                source="rule"
            ))
        
        return custom_tags