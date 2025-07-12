import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging

from ..models.tags import (
    Tag, ContentType, Domain, Priority, Stakeholder
)


logger = logging.getLogger(__name__)


class MLTagger:
    """Machine Learning based tagger using sentence transformers"""
    
    def __init__(self, model_name: str = "sonoisa/sentence-bert-base-ja-mean-tokens-v2"):
        """Initialize ML tagger with a Japanese sentence transformer model"""
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Loaded sentence transformer model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            # Fallback to multilingual model
            self.model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
            logger.info("Using fallback multilingual model")
        
        self._init_reference_texts()
        self._compute_reference_embeddings()
    
    def _init_reference_texts(self):
        """Initialize reference texts for each tag category"""
        
        # Reference texts for content types
        self.content_type_refs = {
            ContentType.DECISION: [
                "本日の会議で以下の事項を決定しました",
                "承認された内容は次の通りです",
                "合意事項として確定しました",
                "決定事項を報告します"
            ],
            ContentType.ISSUE: [
                "以下の課題が発生しています",
                "問題点として挙げられるのは",
                "懸念事項があります",
                "リスクとして認識すべき点"
            ],
            ContentType.ACTION_ITEM: [
                "次回までに完了すべきタスク",
                "担当者は以下を実施してください",
                "アクションアイテムとして対応が必要",
                "期限までに提出をお願いします"
            ],
            ContentType.INFORMATION: [
                "情報共有として報告します",
                "参考情報をお知らせします",
                "連絡事項があります",
                "資料を共有いたします"
            ],
            ContentType.DISCUSSION: [
                "本件について議論が必要です",
                "意見交換を行いました",
                "検討事項として協議します",
                "討議の結果を報告します"
            ]
        }
        
        # Reference texts for domains
        self.domain_refs = {
            Domain.STRUCTURE: [
                "構造計算の結果について",
                "鉄筋コンクリート造の施工",
                "基礎工事の進捗状況",
                "耐震性能の確認"
            ],
            Domain.EQUIPMENT: [
                "設備機器の設置について",
                "空調システムの配管工事",
                "電気設備の配線作業",
                "給排水設備の施工"
            ],
            Domain.CONSTRUCTION_MANAGEMENT: [
                "施工管理の観点から",
                "工程管理について報告",
                "現場監督からの指示",
                "施工計画の変更"
            ],
            Domain.DESIGN: [
                "設計図面の修正について",
                "意匠設計の変更点",
                "詳細図の確認事項",
                "設計変更の承認"
            ],
            Domain.SAFETY: [
                "安全管理の徹底について",
                "労災防止対策の実施",
                "安全パトロールの結果",
                "危険箇所の改善"
            ],
            Domain.QUALITY: [
                "品質管理の観点から",
                "検査結果の報告",
                "品質基準の確認",
                "不良箇所の是正"
            ],
            Domain.COST: [
                "コスト管理について",
                "予算超過の懸念",
                "追加費用の見積もり",
                "コスト削減の提案"
            ],
            Domain.SCHEDULE: [
                "工程表の見直し",
                "スケジュール調整について",
                "工期短縮の検討",
                "マイルストーンの確認"
            ]
        }
        
        # Reference texts for priorities
        self.priority_refs = {
            Priority.HIGH: [
                "至急対応が必要です",
                "最優先で処理してください",
                "緊急度が高い案件",
                "即座に対応をお願いします"
            ],
            Priority.MEDIUM: [
                "通常の優先度で対応",
                "標準的な処理でお願いします",
                "今週中に対応予定",
                "順次処理を進めます"
            ],
            Priority.LOW: [
                "急ぎではありません",
                "時間があるときに対応",
                "参考情報として共有",
                "後回しでも問題ありません"
            ]
        }
        
        # Reference texts for stakeholders
        self.stakeholder_refs = {
            Stakeholder.CLIENT: [
                "発注者からの要望",
                "施主の意向を確認",
                "クライアントとの打ち合わせ",
                "建築主の承認が必要"
            ],
            Stakeholder.DESIGNER: [
                "設計者からの指示",
                "設計事務所との協議",
                "建築家の意見",
                "設計士による確認"
            ],
            Stakeholder.CONTRACTOR: [
                "施工者として対応",
                "ゼネコンの責任範囲",
                "建設会社からの報告",
                "元請業者の判断"
            ],
            Stakeholder.SUPERVISOR: [
                "監理者の確認が必要",
                "工事監理の観点から",
                "現場監督の指示",
                "監理事務所との調整"
            ],
            Stakeholder.SUBCONTRACTOR: [
                "協力業者への依頼",
                "専門工事業者の作業",
                "下請け会社との調整",
                "職人の手配について"
            ]
        }
    
    def _compute_reference_embeddings(self):
        """Compute embeddings for all reference texts"""
        self.embeddings = {}
        
        # Compute embeddings for each category
        for category, refs_dict in [
            ("content_type", self.content_type_refs),
            ("domain", self.domain_refs),
            ("priority", self.priority_refs),
            ("stakeholder", self.stakeholder_refs)
        ]:
            self.embeddings[category] = {}
            for key, texts in refs_dict.items():
                # Compute embeddings for all reference texts
                embeddings = self.model.encode(texts)
                # Store the mean embedding as representative
                self.embeddings[category][key] = np.mean(embeddings, axis=0)
    
    def tag_content(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Apply ML-based tagging to text content"""
        # Encode the input text
        text_embedding = self.model.encode([text])[0]
        
        tags = {
            "content_type": None,
            "domains": [],
            "priority": None,
            "stakeholders": [],
            "custom_tags": []
        }
        
        # Predict content type
        content_type, content_confidence = self._predict_category(
            text_embedding, "content_type", threshold=0.6
        )
        if content_type:
            tags["content_type"] = content_type
            tags["custom_tags"].append(Tag(
                category="ml_confidence",
                value=f"content_type:{content_confidence:.2f}",
                confidence=content_confidence,
                source="ml"
            ))
        
        # Predict domains (can have multiple)
        domains = self._predict_multiple_categories(
            text_embedding, "domain", threshold=0.5, max_items=3
        )
        tags["domains"] = [domain for domain, _ in domains]
        for domain, confidence in domains:
            tags["custom_tags"].append(Tag(
                category="ml_confidence",
                value=f"domain_{domain.value}:{confidence:.2f}",
                confidence=confidence,
                source="ml"
            ))
        
        # Predict priority
        priority, priority_confidence = self._predict_category(
            text_embedding, "priority", threshold=0.5
        )
        if priority:
            tags["priority"] = priority
            tags["custom_tags"].append(Tag(
                category="ml_confidence",
                value=f"priority:{priority_confidence:.2f}",
                confidence=priority_confidence,
                source="ml"
            ))
        
        # Predict stakeholders (can have multiple)
        stakeholders = self._predict_multiple_categories(
            text_embedding, "stakeholder", threshold=0.5, max_items=3
        )
        tags["stakeholders"] = [stakeholder for stakeholder, _ in stakeholders]
        for stakeholder, confidence in stakeholders:
            tags["custom_tags"].append(Tag(
                category="ml_confidence",
                value=f"stakeholder_{stakeholder.value}:{confidence:.2f}",
                confidence=confidence,
                source="ml"
            ))
        
        # Add overall confidence tag
        overall_confidence = self._calculate_overall_confidence(tags)
        tags["custom_tags"].append(Tag(
            category="ml_confidence",
            value=f"overall:{overall_confidence:.2f}",
            confidence=overall_confidence,
            source="ml"
        ))
        
        return tags
    
    def _predict_category(
        self, 
        text_embedding: np.ndarray, 
        category: str, 
        threshold: float = 0.5
    ) -> Tuple[Optional[Any], float]:
        """Predict single category with confidence"""
        embeddings_dict = self.embeddings[category]
        
        best_match = None
        best_score = 0.0
        
        for key, ref_embedding in embeddings_dict.items():
            similarity = cosine_similarity(
                [text_embedding], [ref_embedding]
            )[0][0]
            
            if similarity > best_score:
                best_score = similarity
                best_match = key
        
        if best_score >= threshold:
            return best_match, best_score
        return None, 0.0
    
    def _predict_multiple_categories(
        self, 
        text_embedding: np.ndarray, 
        category: str, 
        threshold: float = 0.5,
        max_items: int = 3
    ) -> List[Tuple[Any, float]]:
        """Predict multiple categories with confidence scores"""
        embeddings_dict = self.embeddings[category]
        
        scores = []
        for key, ref_embedding in embeddings_dict.items():
            similarity = cosine_similarity(
                [text_embedding], [ref_embedding]
            )[0][0]
            
            if similarity >= threshold:
                scores.append((key, similarity))
        
        # Sort by confidence and return top items
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:max_items]
    
    def _calculate_overall_confidence(self, tags: Dict[str, Any]) -> float:
        """Calculate overall confidence score for the tagging"""
        confidence_scores = []
        
        # Extract confidence scores from custom tags
        for tag in tags.get("custom_tags", []):
            if tag.category == "ml_confidence" and "overall" not in tag.value:
                confidence_scores.append(tag.confidence)
        
        if confidence_scores:
            return np.mean(confidence_scores)
        return 0.0