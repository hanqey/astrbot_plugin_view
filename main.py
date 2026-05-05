from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.star.star import star_registry 

@register(
    "astrbot_plugin_view",
    "hansey",
    "一个查看已激活/未激活插件的轻量工具",
    "0.1.0",
    "https://github.com/hanqey/astrbot_plugin_view"
)
class PluginController(Star):
    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)

    # ---------- 消息文本提取 ----------
    def _extract_text(self, event: AstrMessageEvent) -> str:
        msg_obj = event.message_obj
        raw = getattr(msg_obj, "message", None)
        if isinstance(raw, list):
            parts = []
            for seg in raw:
                if hasattr(seg, "text"):
                    parts.append(seg.text)
                elif isinstance(seg, str):
                    parts.append(seg)
                elif isinstance(seg, dict):
                    parts.append(seg.get("text", ""))
            return "".join(parts).strip()
        elif isinstance(raw, str):
            return raw.strip()
        for attr in ("get_plaintext", "message_chain"):
            if hasattr(msg_obj, attr):
                try:
                    return str(getattr(msg_obj, attr)()).strip()
                except:
                    pass
        return ""

    # ---------- 核心命令 ----------
    @filter.command("plugin")
    async def plugin_control(self, event: AstrMessageEvent):
        raw_msg = self._extract_text(event)
        parts = raw_msg.split()
        action = parts[1] if len(parts) > 1 else None

        if not action:
            yield event.plain_result(
                "📋 **插件查看命令**\n"
                "/plugin list — 显示已激活的插件\n"
                "/plugin inactive — 显示未激活的插件"
            )
            return

        if action == "list":
            yield event.plain_result(self._get_plugin_list(active_only=True))
        elif action == "inactive":
            yield event.plain_result(self._get_plugin_list(active_only=False))
        else:
            yield event.plain_result("❌ 不支持的操作。请使用 list 或 inactive。")

    def _get_plugin_list(self, active_only: bool) -> str:
        """构建插件列表字符串"""
        active_plugins = []
        inactive_plugins = []

        try:
            for meta in star_registry:
                if getattr(meta, "reserved", False):
                    continue
                name = getattr(meta, "name", "unknown")
                activated = getattr(meta, "activated", None)
                if activated is False:
                    inactive_plugins.append(name)
                else:
                    active_plugins.append(name)
        except Exception as e:
            logger.error(f"获取插件列表失败: {e}")
            return "❌ 无法获取插件列表，请检查控制台。"

        if active_only:
            if not active_plugins:
                return "📭 当前没有已激活的插件。"
            return f"📦 **已激活插件（{len(active_plugins)} 个）** ：\n" + "\n".join(f"- `{name}`" for name in active_plugins)
        else:
            if not inactive_plugins:
                return "📭 当前所有插件都已激活。"
            return f"📦 **未激活插件（{len(inactive_plugins)} 个）** ：\n" + "\n".join(f"- `{name}`" for name in inactive_plugins)