# content/services/conversation_orchestrator.py

from collections import Counter
import json
import re
from typing import Optional, Dict, Any, List

from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone

from ai.prompts.interview_prompts import InterviewPrompts
from ai.services.ai_service import AIService

from campaigns.models import Campaign, CampaignGoal
from content.models import AIChatSession, AIMessage, ContentItem
from platforms.models import Platform
from research.models import ResearchSource


class ConversationOrchestrator:

    STAGES = {
        "greeting": "خوش‌آمدگویی",
        "platform_selection": "انتخاب پلتفرم",
        "goal_selection": "انتخاب هدف",
        "content_details": "جزئیات محتوا",
        "research": "تحقیق",
        "final_confirmation": "تایید نهایی",
        "content_generation": "تولید محتوا",
        "completed": "تکمیل شده",
    }

    PLATFORM_MAP = {
        "اینستاگرام": "instagram",
        "instagram": "instagram",

        "لینکدین": "linkedin",
        "linkedin": "linkedin",

        "تلگرام": "telegram",
        "telegram": "telegram",

        "توییتر": "twitter",
        "تویتر": "twitter",
        "twitter": "twitter",

        "فیسبوک": "facebook",
        "facebook": "facebook",

        "یوتیوب": "youtube",
        "youtube": "youtube",

        "وب سایت": "website",
        "وب‌سایت": "website",
        "website": "website",

        "وبلاگ": "blog",
        "blog": "blog",
    }

    QUICK_GREETINGS = {
        "سلام",
        "درود",
        "صبح بخیر",
        "عصر بخیر",
        "hello",
        "hi",
    }

    CONFIRM_WORDS = {
        "بله",
        "آره",
        "باشه",
        "اوکی",
        "ادامه",
        "تایید",
        "تایید نهایی",
        "yes",
        "ok",
    }

    GENERATE_WORDS = {
        "بساز",
        "بده",
        "تولید کن",
        "خروجی",
        "ادامه",
        "شروع",
        "generate",
        "create",
    }

    SKIP_WORDS = {
        "نه",
        "رد",
        "skip",
        "no",
        "بدون تحقیق",
    }

    def __init__(
        self,
        user: User,
        session: Optional[AIChatSession] = None,
        content_item: Optional[ContentItem] = None,
        campaign: Optional[Campaign] = None,
    ):

        self.user = user
        self.session = session
        self.content_item = content_item or getattr(
            session,
            "content_item",
            None,
        )

        self.campaign = (
            campaign
            or getattr(self.content_item, "campaign", None)
        )

        self.ai_service = AIService()

    # =========================================================
    # MAIN
    # =========================================================

    def process_message(
        self,
        user_message: str,
    ) -> Dict[str, Any]:

        try:

            self.session = (
                self.session
                or self._create_session()
            )

            if self.session and not self.content_item:
                self.content_item = self.session.content_item

            normalized_message = (
                user_message
                .strip()
                .lower()
            )

            self._save_message(
                user_message,
                "user",
            )

            # =====================================================
            # GREETING
            # =====================================================

            if (
                self._quick_intent_check(user_message)
                == "greeting"
                and not self.content_item
            ):

                response = self._handle_greeting()

                self._save_message(
                    response["message"],
                    "assistant",
                )
                print(type(response))
                print(response)
                return self._build_final_response(response)

            # =====================================================
            # AUTO CREATE CONTENT ITEM
            # =====================================================

            if not self.content_item:
                self._create_content_item({
                    "title": "محتوای جدید"
                })

            # =====================================================
            # DETECT STAGE
            # =====================================================

            stage = self._detect_current_stage()

            # =====================================================
            # RESEARCH STAGE
            # =====================================================

            if stage == "research":

                response = self._handle_research_stage_message(
                    user_message
                )

                self._save_message(
                    response["message"],
                    "assistant",
                )

                return self._build_final_response(response)

            # =====================================================
            # FINAL CONFIRMATION
            # =====================================================

            if (
                stage == "final_confirmation"
                and any(
                    word in normalized_message
                    for word in self.GENERATE_WORDS
                )
            ):

                article = self._generate_content()

                response = {
                    "message": article,
                    "quick_replies": [],
                    "orders": [],
                }

                self._save_message(
                    article,
                    "assistant",
                )

                return self._build_final_response(response)

            # =====================================================
            # COMPLETED
            # =====================================================

            if stage == "completed":

                response = {
                    "message": (
                        "این محتوا قبلاً تولید شده است."
                    ),
                    "quick_replies": [],
                    "orders": [],
                }

                return self._build_final_response(response)

            # =====================================================
            # AI FLOW
            # =====================================================

            backend_context = self._build_backend_context()

            messages = [
                {
                    "role": "system",
                    "content": InterviewPrompts.get_system_prompt(
                        backend_context
                    ),
                },

                *self._get_conversation_history(),

                {
                    "role": "user",
                    "content": InterviewPrompts.get_user_prompt(
                        user_message,
                        backend_context,
                    ),
                },
            ]

            ai_response = self.ai_service.chat(
                messages=messages,
                temperature=0.3,
                max_tokens=1200,
                response_format="json",
            )

            print("\n========== AI RESPONSE ==========")
            print(ai_response)
            print("=================================\n")

            parsed = self._parse_ai_response(ai_response)

            self._execute_orders(
                parsed.get("orders", [])
            )

            if self.content_item:
                self.content_item.refresh_from_db()

            stage_after_orders = self._detect_current_stage()

            # =====================================================
            # AUTO ASK RESEARCH
            # =====================================================

            if stage_after_orders == "research":

                response = {
                    "message": (
                        "آیا تحقیق روی موضوع انجام شود؟"
                    ),
                    "quick_replies": [
                        {
                            "label": "بله",
                            "value": "بله",
                        },
                        {
                            "label": "نه",
                            "value": "نه",
                        },
                    ],
                    "orders": [],
                }

                self._save_message(
                    response["message"],
                    "assistant",
                )

                return self._build_final_response(response)

            # =====================================================
            # AUTO FINAL CONFIRMATION
            # =====================================================

            if stage_after_orders == "final_confirmation":

                response = {
                    "message": (
                        "خلاصه اطلاعات فعلی:\n\n"
                        f"• پلتفرم: {self.content_item.platform}\n"
                        f"• هدف: {self.content_item.goal}\n"
                        f"• عنوان: {self.content_item.title}\n\n"
                        "اگر تایید می‌کنید بگویید:\n"
                        "«بساز»"
                    ),
                    "quick_replies": [
                        {
                            "label": "بساز",
                            "value": "بساز",
                        }
                    ],
                    "orders": [],
                }

                self._save_message(
                    response["message"],
                    "assistant",
                )

                return self._build_final_response(response)

            # =====================================================
            # NORMAL RESPONSE
            # =====================================================

            self._save_message(
                parsed["message"],
                "assistant",
            )

            return self._build_final_response(parsed)

        except Exception as e:

            print(f"❌ process_message error: {e}")

            return self._build_error_response()

    # =========================================================
    # CONTEXT
    # =========================================================

    def _build_backend_context(self):

        completed = self._get_completed_fields()

        return {
            "current_stage": self._detect_current_stage(),

            "completed_fields": completed,

            "missing_fields": [
                field
                for field in [
                    "platform",
                    "goal",
                    "title",
                ]
                if field not in completed
            ],

            "available_platforms":
                self._get_available_platforms(),

            "available_goals":
                self._get_available_goals(),
        }

    def _detect_current_stage(self) -> str:

        if not self.content_item:
            return "greeting"

        status = (
                self.content_item.status or ""
        ).strip().lower()

        if status == "completed":
            return "completed"

        info = self.content_item.information or {}
        metadata = self.content_item.metadata or {}

        platform = str(
            self.content_item.platform or ""
        ).strip()

        goal = str(
            self.content_item.goal or ""
        ).strip()

        title = str(
            self.content_item.title or ""
        ).strip()

        # =========================================
        # PLATFORM
        # =========================================

        if not platform:
            return "platform_selection"

        # =========================================
        # GOAL
        # =========================================

        if not goal:
            return "goal_selection"

        # =========================================
        # TITLE
        # =========================================

        if title in [
            "",
            "محتوای جدید",
            "untitled",
        ]:
            return "content_details"

        # =========================================
        # REQUIRED CONTENT DETAILS
        # =========================================

        required_fields = {

            "target_audience":
                metadata.get("target_audience"),

            "tone":
                metadata.get("tone"),
        }

        missing = [

            k for k, v in required_fields.items()

            if not str(v or "").strip()
        ]

        if missing:
            return "content_details"

        # =========================================
        # RESEARCH
        # =========================================

        research = info.get("research", [])

        skipped = metadata.get(
            "research_skipped",
            False,
        )

        if not research and not skipped:
            return "research"

        # =========================================
        # GENERATING
        # =========================================

        if status == "generating":
            return "content_generation"

        return "final_confirmation"

    def _get_completed_fields(self):

        if not self.content_item:
            return {}

        metadata = self.content_item.metadata or {}

        fields = {
            "platform": self.content_item.platform,
            "goal": self.content_item.goal,
            "title": self.content_item.title,
            "main_keyword":
                self.content_item.main_keyword,
            "keywords":
                metadata.get("keywords"),
            "tone":
                metadata.get("tone"),
            "target_audience":
                metadata.get("target_audience"),
            "length":
                metadata.get("length"),
        }

        return {
            k: v
            for k, v in fields.items()
            if v
            and v not in [
                "untitled",
                "محتوای جدید",
            ]
        }

    # =========================================================
    # AI RESPONSE
    # =========================================================

    def _parse_ai_response(
            self,
            response: str,
    ) -> Dict[str, Any]:

        ALLOWED_ACTIONS = {

            "UPDATE_CONTENT_ITEM",
            "CREATE_CONTENT_ITEM",
            "UPDATE_CONTENT_DETAILS",
            "UPDATE_PLATFORM",
            "UPDATE_GOAL",
            "START_RESEARCH",
            "GENERATE_RESEARCH",
            "SKIP_RESEARCH",
            "GENERATE_CONTENT",
        }

        try:

            parsed = json.loads(response)

            if isinstance(parsed, list):

                if (
                        len(parsed) > 0
                        and isinstance(parsed[0], dict)
                ):
                    parsed = parsed[0]

                else:
                    parsed = {}

            if not isinstance(parsed, dict):
                parsed = {}

            message = str(
                parsed.get("message", "")
            ).strip()

            orders = parsed.get(
                "orders",
                [],
            )

            if not isinstance(orders, list):
                orders = []

            validated_orders = []

            for order in orders:

                if not isinstance(order, dict):
                    continue

                action = str(
                    order.get("action", "")
                ).upper().strip()

                if action not in ALLOWED_ACTIONS:
                    continue

                validated_orders.append(order)

            quick_replies = parsed.get(
                "quick_replies",
                [],
            )

            if not isinstance(
                    quick_replies,
                    list,
            ):
                quick_replies = []

            cleaned_quick_replies = []

            for item in quick_replies:

                if not isinstance(item, dict):
                    continue

                label = str(
                    item.get("label", "")
                ).strip()

                value = str(
                    item.get("value", "")
                ).strip()

                if not label or not value:
                    continue

                cleaned_quick_replies.append({
                    "label": label,
                    "value": value,
                })

            return {

                "message": message,

                "orders": validated_orders,

                "quick_replies":
                    cleaned_quick_replies,
            }

        except Exception as e:

            print(
                f"❌ parse ai response error: {e}"
            )

            return {

                "message": str(response),

                "orders": [],

                "quick_replies": [],
            }

    # =========================================================
    # ORDERS
    # =========================================================

    def _execute_orders(
            self,
            orders: List[Dict[str, Any]],
    ):

        handlers = {

            "UPDATE_CONTENT_ITEM":
                self._handle_update_content_item,

            "CREATE_CONTENT_ITEM":
                self._handle_create_content_item,

            "UPDATE_CONTENT_DETAILS":
                self._handle_update_content_details,

            "UPDATE_PLATFORM":
                self._handle_legacy_platform,

            "UPDATE_GOAL":
                self._handle_legacy_goal,

            "START_RESEARCH":
                lambda _: self.start_research(),

            "GENERATE_RESEARCH":
                lambda _: self.start_research(),

            "SKIP_RESEARCH":
                lambda _: self._skip_research(),

            "GENERATE_CONTENT":
                lambda _: self._generate_content(),
        }

        for order in orders:

            if not isinstance(order, dict):
                continue

            action = str(
                order.get("action", "")
            ).upper().strip()

            if not action:
                continue

            try:

                handler = handlers.get(action)

                if not handler:
                    print(
                        f"⚠️ Unknown action: {action}"
                    )
                    continue

                handler(order)

            except Exception as e:

                print(
                    f"❌ order error [{action}]: {e}"
                )

                if self.content_item:
                    self.content_item.status = "error"

                    self.content_item.save(
                        update_fields=["status"]
                    )

    # =========================================================
    # ORDER HANDLERS
    # =========================================================

    def _handle_update_content_item(self, order):

        self._update_content_field(
            order.get("field"),
            order.get("value"),
        )

    def _handle_create_content_item(self, order):

        self._create_content_item(
            order.get("data") or {}
        )

    def _handle_update_content_details(self, order):

        self._update_content_details(
            order.get("data") or {}
        )

    def _handle_legacy_platform(self, order):

        platform_id = (
            order.get("data") or {}
        ).get("platform_id")

        self._update_platform(platform_id)

    def _handle_legacy_goal(self, order):

        goal_id = (
            order.get("data") or {}
        ).get("goal_id")

        self._update_goal(goal_id)

    # =========================================================
    # UPDATE METHODS
    # =========================================================

    def _update_content_field(
        self,
        field: str,
        value: Any,
    ):

        if not self.content_item or not field:
            return

        metadata_fields = {
            "keywords",
            "tone",
            "target_audience",
            "length",
        }

        try:

            if field == "platform":

                platform = self._find_platform_by_name(
                    value
                )

                if platform:
                    self.content_item.platform = (
                        platform.name
                    )

                else:
                    self.content_item.platform = str(
                        value
                    )

            elif field == "goal":

                goal = self._find_goal_by_name(
                    value
                )

                if goal:
                    self.content_item.goal = goal.goal
                else:
                    self.content_item.goal = str(value)

            elif field in metadata_fields:

                metadata = (
                    self.content_item.metadata
                    or {}
                )

                metadata[field] = (
                    self._normalize_keywords(value)
                    if field == "keywords"
                    else str(value).strip()
                )

                self.content_item.metadata = metadata

            elif hasattr(self.content_item, field):

                setattr(
                    self.content_item,
                    field,
                    str(value).strip()
                    if isinstance(value, str)
                    else value,
                )

            self.content_item.save()

        except Exception as e:

            print(
                f"❌ update field error [{field}]: {e}"
            )

    def _update_content_details(
        self,
        data: Dict[str, Any],
    ):

        for field, value in data.items():
            self._update_content_field(
                field,
                value,
            )

    def _update_platform(
        self,
        platform_id: str,
    ):

        if not platform_id:
            return

        platform = Platform.objects.filter(
            id=platform_id
        ).first()

        if platform:
            self._update_content_field(
                "platform",
                platform.name,
            )

    def _update_goal(
        self,
        goal_id: str,
    ):

        if not goal_id:
            return

        goal = CampaignGoal.objects.filter(
            id=goal_id
        ).first()

        if goal:
            self._update_content_field(
                "goal",
                goal.goal,
            )

    # =========================================================
    # CONTENT ITEM
    # =========================================================

    def _create_content_item(
            self,
            data: Dict[str, Any],
    ):

        if self.content_item:
            return

        try:

            create_data = {
                "title": data.get(
                    "title",
                    "محتوای جدید",
                ),
                "status": "draft",
                "step": "interview",
                "metadata": {},
                "information": {},
            }

            # فقط اگر کمپین وجود داشت ست شود
            if self.campaign:
                create_data["campaign"] = self.campaign

            # اگر مدل platform required بود
            if hasattr(ContentItem, "platform"):
                create_data["platform"] = "website"

            # اگر مدل language داشت
            if hasattr(ContentItem, "language"):
                create_data["language"] = "fa"

            self.content_item = ContentItem.objects.create(
                **create_data
            )

            if self.session:
                self.session.content_item = (
                    self.content_item
                )

                self.session.save(
                    update_fields=["content_item"]
                )

        except Exception as e:

            print(
                f"❌ create content item error: {e}"
            )

    # =========================================================
    # RESEARCH
    # =========================================================

    def _handle_research_stage_message(
        self,
        user_message: str,
    ):

        text = user_message.lower().strip()

        # =====================================================
        # START RESEARCH
        # =====================================================

        if any(
            word in text
            for word in self.CONFIRM_WORDS
        ):

            result = self.start_research()

            if result["success"]:

                count = result.get(
                    "sources_count",
                    0,
                )

                return {
                    "message": (
                        f"✅ تحقیق انجام شد.\n"
                        f"{count} منبع مرتبط پیدا شد.\n\n"
                        "اگر آماده هستید بگویید:\n"
                        "«بساز»"
                    ),
                    "quick_replies": [
                        {
                            "label": "بساز",
                            "value": "بساز",
                        }
                    ],
                    "orders": [],
                }

            return {
                "message":
                    "خطا در انجام تحقیق.",
                "quick_replies": [],
                "orders": [],
            }

        # =====================================================
        # SKIP RESEARCH
        # =====================================================

        if any(
            word in text
            for word in self.SKIP_WORDS
        ):

            self._skip_research()

            return {
                "message": (
                    "تحقیق رد شد.\n\n"
                    "اگر می‌خواهید محتوا تولید شود "
                    "بگویید:\n"
                    "«بساز»"
                ),
                "quick_replies": [
                    {
                        "label": "بساز",
                        "value": "بساز",
                    }
                ],
                "orders": [],
            }

        return {
            "message":
                "آیا تحقیق انجام شود؟",

            "quick_replies": [
                {
                    "label": "بله",
                    "value": "بله",
                },
                {
                    "label": "نه",
                    "value": "نه",
                },
            ],

            "orders": [],
        }

    def start_research(self):

        if not self.content_item:

            return {
                "success": False,
                "message":
                    "content item not found",
            }

        try:

            query = self._build_research_query()

            if not query.strip():

                return {
                    "success": False,
                    "message":
                        "empty query",
                }

            sources = self._search_sources(query)

            research_data = []

            for src in sources:

                research_data.append({
                    "id": src.id,
                    "title":
                        (src.title or "").strip(),

                    "summary":
                        (src.summary or "").strip(),

                    "raw_text":
                        (src.raw_text or "")[:4000],

                    "url":
                        getattr(src, "url", ""),

                    "source_type":
                        getattr(
                            src,
                            "source_type",
                            "",
                        ),
                })

            information = (
                self.content_item.information
                or {}
            )

            information["research"] = (
                research_data
            )

            information["research_query"] = (
                query
            )

            information[
                "research_generated_at"
            ] = timezone.now().isoformat()

            self.content_item.information = (
                information
            )

            self.content_item.status = (
                "research_done"
            )

            self.content_item.save()

            return {
                "success": True,
                "sources_count":
                    len(research_data),
            }

        except Exception as e:

            print(f"❌ research error: {e}")

            return {
                "success": False,
                "message": str(e),
            }

    def _skip_research(self):

        if not self.content_item:
            return

        metadata = (
            self.content_item.metadata
            or {}
        )

        metadata["research_skipped"] = True

        self.content_item.metadata = metadata

        self.content_item.status = (
            "research_skipped"
        )

        self.content_item.save()

    def _build_research_query(self):

        if not self.content_item:
            return ""

        metadata = self.content_item.metadata or {}

        parts = []

        if self.content_item.title:
            parts.append(
                self.content_item.title
            )

        if self.content_item.main_keyword:
            parts.append(
                self.content_item.main_keyword
            )

        keywords = (
            metadata.get("keywords")
            or []
        )

        if isinstance(keywords, list):
            parts.extend(keywords)

        if metadata.get("target_audience"):
            parts.append(
                metadata.get(
                    "target_audience"
                )
            )

        cleaned = []

        for item in parts:

            value = str(item).strip()

            if value and value not in cleaned:
                cleaned.append(value)

        return " | ".join(cleaned)

    def _search_sources(self, query: str):

        keywords = [

            k.strip().lower()

            for k in re.split(
                r"[\s\|\-_,]+",
                query,
            )

            if len(k.strip()) >= 2
        ]

        if not keywords:
            return ResearchSource.objects.none()

        keyword_counter = Counter(keywords)

        db_query = Q()

        for keyword in keywords:
            db_query |= (
                    Q(title__icontains=keyword)
                    | Q(summary__icontains=keyword)
                    | Q(raw_text__icontains=keyword)
            )

        queryset = (

            ResearchSource.objects
            .filter(db_query)
            .distinct()[:200]

        )

        scored_items = []

        for source in queryset:

            score = 0

            haystack = " ".join([

                source.title or "",
                source.summary or "",
                source.raw_text or "",

            ]).lower()

            for keyword, weight in (
                    keyword_counter.items()
            ):

                if keyword in haystack:
                    score += weight

            if score > 0:
                scored_items.append(
                    (score, source)
                )

        scored_items.sort(

            key=lambda x: (

                x[0],

                getattr(
                    x[1],
                    "created_at",
                    timezone.now(),
                ),

            ),

            reverse=True,
        )

        return [
            item[1]
            for item in scored_items[:20]
        ]

    # =========================================================
    # GENERATION
    # =========================================================

    def _generate_content(self):

        if not self.content_item:
            return "خطا در تولید محتوا."

        try:

            self.content_item.status = (
                "generating"
            )

            self.content_item.save(
                update_fields=["status"]
            )

            metadata = (
                self.content_item.metadata
                or {}
            )

            research_text = (
                self._build_research_text()
            )

            article = (
                self.ai_service.generate_article(
                    title=(
                        self.content_item.title
                        or ""
                    ),

                    description=f"""
پلتفرم:
{self.content_item.platform}

هدف:
{self.content_item.goal}

مخاطب هدف:
{metadata.get("target_audience", "")}

لحن:
{metadata.get("tone", "")}
                    """,

                    research=research_text,

                    platform=str(
                        self.content_item.platform
                        or ""
                    ),

                    keywords=metadata.get(
                        "keywords",
                        [],
                    ),
                )
            )

            if not article:
                article = (
                    "خطا در تولید محتوا."
                )

            if hasattr(
                self.content_item,
                "generated_content",
            ):

                self.content_item.generated_content = (
                    article
                )

            elif hasattr(
                self.content_item,
                "content",
            ):

                self.content_item.content = (
                    article
                )

            else:

                info = (
                    self.content_item.information
                    or {}
                )

                info["generated_content"] = (
                    article
                )

                self.content_item.information = (
                    info
                )

            self.content_item.status = (
                "completed"
            )

            self.content_item.save()

            return article

        except Exception as e:

            print(
                f"❌ generate content error: {e}"
            )

            self.content_item.status = "error"

            self.content_item.save(
                update_fields=["status"]
            )

            return "خطا در تولید محتوا."

    def _build_research_text(self):

        info = self.content_item.information or {}

        research = info.get("research", [])

        if not research:
            return ""

        chunks = []

        for item in research:

            if not isinstance(item, dict):
                continue

            title = item.get("title", "")
            summary = item.get("summary", "")
            raw_text = item.get("raw_text", "")

            text_parts = [
                f"TITLE:\n{title}",
                f"SUMMARY:\n{summary}",
            ]

            if raw_text:

                text_parts.append(
                    f"CONTENT:\n{raw_text[:1500]}"
                )

            chunks.append(
                "\n".join(text_parts)
            )

        return (
            "\n\n------------------\n\n"
            .join(chunks)
        )

    # =========================================================
    # HELPERS
    # =========================================================

    def _quick_intent_check(
        self,
        message: str,
    ):

        text = message.lower().strip()

        if (
            text in self.QUICK_GREETINGS
            or (
                len(text.split()) <= 3
                and any(
                    g in text
                    for g in self.QUICK_GREETINGS
                )
            )
        ):
            return "greeting"

        return None

    def _find_platform_by_name(
        self,
        name: str,
    ):

        if not name:
            return None

        normalized = self.PLATFORM_MAP.get(
            str(name).strip(),
            str(name).lower().strip(),
        )

        return Platform.objects.filter(
            name__iexact=normalized,
            is_active=True,
        ).first()

    def _find_goal_by_name(
        self,
        name: str,
    ):

        if not name:
            return None

        return (
            CampaignGoal.objects
            .filter(
                Q(goal__iexact=name.strip())
                | Q(goal__icontains=name.strip()),
                is_active=True,
            )
            .first()
        )

    def _normalize_keywords(self, value):

        if isinstance(value, list):

            return [
                str(v).strip()
                for v in value
                if str(v).strip()
            ]

        if isinstance(value, str):

            return [
                v.strip()
                for v in value.split(",")
                if v.strip()
            ]

        return []

    # =========================================================
    # DATABASE
    # =========================================================

    def _get_available_platforms(self):

        return [
            {
                "id": str(p.id),
                "name": p.name,
                "label":
                    self._get_platform_persian_name(
                        p.name
                    ),
            }

            for p in Platform.objects.filter(
                is_active=True,
                is_open=True,
            )
        ]

    def _get_available_goals(self):

        return [
            {
                "id": str(g.id),
                "name": g.goal,
                "label": g.goal,
            }

            for g in CampaignGoal.objects.filter(
                is_active=True
            )
        ]

    def _get_platform_persian_name(
        self,
        name: str,
    ):

        reverse = {
            v: k
            for k, v
            in self.PLATFORM_MAP.items()
        }

        return reverse.get(
            name.lower(),
            name,
        )

    def _get_conversation_history(self):

        if not self.session:
            return []

        messages = list(

            AIMessage.objects
            .filter(session=self.session)
            .order_by("-created_at")[:10]

        )

        messages.reverse()

        return [

            {
                "role": msg.role,
                "content": msg.content,
            }

            for msg in messages
        ]

    def _save_message(
            self,
            content: str,
            role: str,
    ):

        if not self.session or not content:
            return

        try:

            last_message = (
                AIMessage.objects
                .filter(
                    session=self.session,
                    role=role,
                )
                .order_by("-created_at")
                .first()
            )

            # جلوگیری از ذخیره تکراری
            if (
                    last_message
                    and last_message.content.strip() == content.strip()
            ):
                return

            AIMessage.objects.create(
                session=self.session,
                role=role,
                content=content,
            )

        except Exception as e:

            print(f"❌ save message error: {e}")


    def _create_session(self):

        return AIChatSession.objects.create(
            user=self.user,
            content_item=self.content_item,
        )

    # =========================================================
    # RESPONSES
    # =========================================================

    def _handle_greeting(self):

        return {

            "message": (
                "سلام 👋\n\n"
                "برای کدام پلتفرم "
                "می‌خواهی محتوا تولید کنیم؟"
            ),

            "quick_replies": [

                {
                    "label": p["label"],
                    "value": p["name"],
                }

                for p in self._get_available_platforms()
            ],

            "orders": [],
        }

    def _build_final_response(self, response):

        if not isinstance(response, dict):
            print("❌ invalid response type:", type(response))
            print(response)

            response = {
                "message": "خطا در پردازش پاسخ.",
                "quick_replies": [],
                "orders": [],
            }

        quick_replies = response.get("quick_replies", [])

        if not isinstance(quick_replies, list):
            quick_replies = []

        orders = response.get("orders", [])

        if not isinstance(orders, list):
            orders = []

        return {
            "success": True,
            "message": response.get("message", ""),
            "quick_replies": quick_replies,
            "orders": orders,
            "stage": self._detect_current_stage(),
            "content_item_id": getattr(
                self.content_item,
                "id",
                None,
            ),
            "session_id": getattr(
                self.session,
                "id",
                None,
            ),
        }

    def _build_error_response(self):

        return {

            "success": False,

            "message": (
                "متاسفانه خطایی "
                "در پردازش پیام رخ داد."
            ),

            "quick_replies": [],

            "orders": [],
        }