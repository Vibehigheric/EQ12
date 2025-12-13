#!/usr/bin/env python3
"""
EQ12 Discord Integration Bot

Creates dual Discord architecture:
1. Private Ops Server (Mission Control) - Admin/team coordination
2. Public Community Server - Affiliate funnel + premium content

Integrates with:
- EQ12 Telegram Master Bot (cross-posting)
- Apple TV Command Center (content distribution)
- Snip Watcher (visual data sharing)
- EQ12 APIs (betting, travel, finance)
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

try:
    import aiohttp
    import discord
    from discord.ext import commands, tasks

    DISCORD_AVAILABLE = True
except ImportError as e:
    DISCORD_AVAILABLE = False
    print(f"[ERROR] Missing Discord dependencies: {e}")
    print("Install: pip install discord.py aiohttp")

# EQ12 Configuration
EQ12_HOME = Path(os.getenv("EQ12_HOME", r"C:\EQ12"))
DISCORD_LOGS_DIR = EQ12_HOME / "logs" / "discord_bot"
DISCORD_CONFIG_FILE = EQ12_HOME / "configs" / "discord_config.json"

# Ensure directories exist
DISCORD_LOGS_DIR.mkdir(parents=True, exist_ok=True)


class ServerType(Enum):
    """Discord server types"""

    OPS = "ops"  # Private mission control
    COMMUNITY = "community"  # Public affiliate funnel


class ChannelType(Enum):
    """Discord channel types"""

    ALERTS = "alerts"
    BETTING = "betting"
    TRAVEL = "travel"
    FINANCE = "finance"
    APPLETV = "appletv"
    SNIPS = "snips"
    GENERAL = "general"
    PREMIUM = "premium"
    AFFILIATE = "affiliate"
    LOGS = "logs"


@dataclass
class DiscordServerConfig:
    """Discord server configuration"""

    server_id: int
    server_type: ServerType
    channels: dict[ChannelType, int]
    roles: dict[str, int]
    webhook_urls: dict[str, str]


@dataclass
class BotMessage:
    """Structured bot message"""

    title: str
    content: str
    embed_color: int = 0x00FF00
    fields: list[dict] = None
    image_url: str | None = None
    thumbnail_url: str | None = None


class EQ12DiscordBot(commands.Bot):
    """EQ12 Discord Bot with dual server support"""

    def __init__(self):
        # Bot configuration
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True

        super().__init__(command_prefix="!eq12 ", intents=intents, help_command=None)

        # Setup logging
        self._setup_logging()

        # Load configuration
        self.config = self._load_config()

        # Server configurations
        self.servers: dict[ServerType, DiscordServerConfig] = {}

        # API endpoints
        self.eq12_api_base = "http://localhost:8000"
        self.telegram_api_base = "http://localhost:8001"
        self.appletv_api_base = "http://localhost:8080"

        # Cross-posting settings
        self.cross_post_enabled = True
        self.premium_role_required = ["premium", "vip", "elite"]

        # Statistics
        self.stats = {
            "messages_sent": 0,
            "commands_executed": 0,
            "cross_posts": 0,
            "start_time": datetime.now(),
        }

    def _setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            handlers=[
                logging.FileHandler(DISCORD_LOGS_DIR / "discord_bot.log", encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger("EQ12DiscordBot")

    def _load_config(self) -> dict:
        """Load Discord configuration"""
        if not DISCORD_CONFIG_FILE.exists():
            # Create default config
            default_config = {
                "ops_server": {
                    "server_id": None,
                    "channels": {
                        "alerts": None,
                        "betting": None,
                        "travel": None,
                        "finance": None,
                        "appletv": None,
                        "snips": None,
                        "logs": None,
                    },
                    "roles": {"admin": None, "operator": None},
                },
                "community_server": {
                    "server_id": None,
                    "channels": {
                        "general": None,
                        "betting": None,
                        "travel": None,
                        "premium": None,
                        "affiliate": None,
                    },
                    "roles": {
                        "premium": None,
                        "vip": None,
                        "elite": None,
                        "affiliate": None,
                    },
                },
                "telegram_integration": {
                    "enabled": True,
                    "cross_post_channels": ["betting", "travel", "alerts"],
                },
                "apple_tv_integration": {
                    "enabled": True,
                    "stream_channels": ["appletv", "premium"],
                },
            }

            with open(DISCORD_CONFIG_FILE, "w") as f:
                json.dump(default_config, f, indent=2)

            self.logger.info(f"Created default config at {DISCORD_CONFIG_FILE}")

        with open(DISCORD_CONFIG_FILE) as f:
            return json.load(f)

    async def setup_hook(self):
        """Setup bot after login"""
        self.logger.info("EQ12 Discord Bot setting up...")

        # Start background tasks
        if not self.sync_with_telegram.is_running():
            self.sync_with_telegram.start()

        if not self.monitor_eq12_apis.is_running():
            self.monitor_eq12_apis.start()

    async def on_ready(self):
        """Bot ready event"""
        self.logger.info(f"EQ12 Discord Bot ready: {self.user}")
        self.logger.info(f"Connected to {len(self.guilds)} servers")

        # Setup server configurations
        await self._setup_servers()

        # Send startup message
        await self._send_startup_message()

    async def _setup_servers(self):
        """Setup server configurations"""
        for guild in self.guilds:
            self.logger.info(f"Setting up server: {guild.name} (ID: {guild.id})")

            # Determine server type based on config
            if self.config["ops_server"]["server_id"] == guild.id:
                server_type = ServerType.OPS
                config_key = "ops_server"
            elif self.config["community_server"]["server_id"] == guild.id:
                server_type = ServerType.COMMUNITY
                config_key = "community_server"
            else:
                self.logger.warning(f"Unknown server: {guild.name}")
                continue

            # Build server config
            server_config = DiscordServerConfig(
                server_id=guild.id,
                server_type=server_type,
                channels={},
                roles={},
                webhook_urls={},
            )

            # Map channel names to IDs
            config_channels = self.config[config_key]["channels"]
            for channel_name, channel_id in config_channels.items():
                if channel_id:
                    try:
                        channel_type = ChannelType(channel_name)
                        server_config.channels[channel_type] = channel_id
                    except ValueError:
                        self.logger.warning(f"Unknown channel type: {channel_name}")

            # Map role names to IDs
            config_roles = self.config[config_key]["roles"]
            for role_name, role_id in config_roles.items():
                if role_id:
                    server_config.roles[role_name] = role_id

            self.servers[server_type] = server_config
            self.logger.info(
                f"Configured {server_type.value} server with {len(server_config.channels)} channels"
            )

    async def _send_startup_message(self):
        """Send startup message to ops server"""
        if ServerType.OPS not in self.servers:
            return

        ops_config = self.servers[ServerType.OPS]
        if ChannelType.LOGS not in ops_config.channels:
            return

        channel = self.get_channel(ops_config.channels[ChannelType.LOGS])
        if not channel:
            return

        embed = discord.Embed(
            title="EQ12 Discord Bot Online",
            description="Multi-server Discord integration active",
            color=0x00FF00,
            timestamp=datetime.now(),
        )

        embed.add_field(name="Servers", value=len(self.guilds), inline=True)
        embed.add_field(name="Commands", value=len(self.commands), inline=True)
        embed.add_field(
            name="Integrations",
            value="Telegram • Apple TV • Snip Watcher",
            inline=False,
        )

        await channel.send(embed=embed)

    # === CORE MESSAGING ===

    async def send_to_channel(
        self,
        server_type: ServerType,
        channel_type: ChannelType,
        message: BotMessage,
        cross_post: bool = True,
    ) -> bool:
        """Send message to specific server/channel"""
        try:
            if server_type not in self.servers:
                self.logger.error(f"Server type {server_type} not configured")
                return False

            server_config = self.servers[server_type]
            if channel_type not in server_config.channels:
                self.logger.error(f"Channel type {channel_type} not found in {server_type}")
                return False

            channel = self.get_channel(server_config.channels[channel_type])
            if not channel:
                self.logger.error(f"Channel not accessible: {server_config.channels[channel_type]}")
                return False

            # Build embed
            embed = discord.Embed(
                title=message.title,
                description=message.content,
                color=message.embed_color,
                timestamp=datetime.now(),
            )

            if message.fields:
                for field in message.fields:
                    embed.add_field(**field)

            if message.image_url:
                embed.set_image(url=message.image_url)

            if message.thumbnail_url:
                embed.set_thumbnail(url=message.thumbnail_url)

            await channel.send(embed=embed)
            self.stats["messages_sent"] += 1

            # Cross-post to Telegram if enabled
            if cross_post and self.cross_post_enabled:
                await self._cross_post_to_telegram(message, channel_type)

            return True

        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False

    async def _cross_post_to_telegram(self, message: BotMessage, channel_type: ChannelType):
        """Cross-post message to Telegram"""
        try:
            if not self.config.get("telegram_integration", {}).get("enabled"):
                return

            cross_post_channels = self.config["telegram_integration"]["cross_post_channels"]
            if channel_type.value not in cross_post_channels:
                return

            # Format for Telegram
            telegram_text = f"**{message.title}**\n\n{message.content}"

            if message.fields:
                for field in message.fields:
                    telegram_text += f"\n\n**{field['name']}**: {field['value']}"

            # Send to Telegram API
            telegram_payload = {
                "text": telegram_text,
                "parse_mode": "Markdown",
                "source": "discord_bot",
            }

            async with (
                aiohttp.ClientSession() as session,
                session.post(
                    f"{self.telegram_api_base}/send_message", json=telegram_payload
                ) as response,
            ):
                if response.status == 200:
                    self.stats["cross_posts"] += 1
                    self.logger.debug(f"Cross-posted to Telegram: {message.title}")
                else:
                    self.logger.warning(f"Telegram cross-post failed: {response.status}")

        except Exception as e:
            self.logger.error(f"Cross-post to Telegram failed: {e}")

    # === COMMANDS ===

    @commands.command(name="status")
    async def status_command(self, ctx):
        """Show bot status"""
        self.stats["commands_executed"] += 1

        uptime = datetime.now() - self.stats["start_time"]

        embed = discord.Embed(
            title="EQ12 Discord Bot Status", color=0x0099FF, timestamp=datetime.now()
        )

        embed.add_field(name="Uptime", value=f"{uptime.total_seconds():.0f}s", inline=True)
        embed.add_field(name="Servers", value=len(self.guilds), inline=True)
        embed.add_field(name="Messages Sent", value=self.stats["messages_sent"], inline=True)
        embed.add_field(
            name="Commands Executed", value=self.stats["commands_executed"], inline=True
        )
        embed.add_field(name="Cross Posts", value=self.stats["cross_posts"], inline=True)
        embed.add_field(name="Latency", value=f"{self.latency * 1000:.1f}ms", inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="parlay")
    async def parlay_command(self, ctx, size: str = "5", sport: str = "nfl"):
        """Generate parlay and post to betting channels"""
        self.stats["commands_executed"] += 1

        try:
            # Call EQ12 parlay API
            async with aiohttp.ClientSession() as session:
                params = {"size": size, "sport": sport}
                async with session.get(
                    f"{self.eq12_api_base}/api/parlay", params=params
                ) as response:
                    if response.status != 200:
                        await ctx.send("❌ Failed to generate parlay")
                        return

                    parlay_data = await response.json()

            # Create Discord message
            message = BotMessage(
                title=f"🎯 {sport.upper()} {size}-Leg Parlay",
                content=parlay_data.get("summary", "Generated new parlay"),
                embed_color=0xFF6B35,
                fields=[
                    {
                        "name": "Legs",
                        "value": str(len(parlay_data.get("legs", []))),
                        "inline": True,
                    },
                    {
                        "name": "Total Odds",
                        "value": parlay_data.get("total_odds", "TBD"),
                        "inline": True,
                    },
                    {
                        "name": "Potential Payout",
                        "value": f"${parlay_data.get('payout', 0)}",
                        "inline": True,
                    },
                ],
            )

            # Send to both servers
            await self.send_to_channel(ServerType.OPS, ChannelType.BETTING, message)
            await self.send_to_channel(ServerType.COMMUNITY, ChannelType.BETTING, message)

            await ctx.send("✅ Parlay posted to betting channels")

        except Exception as e:
            self.logger.error(f"Parlay command failed: {e}")
            await ctx.send("❌ Error generating parlay")

    @commands.command(name="deal")
    async def deal_command(self, ctx, from_city: str = "BUF", to_city: str = "LAX"):
        """Find travel deal and post to travel channels"""
        self.stats["commands_executed"] += 1

        try:
            # Call EQ12 travel API
            async with aiohttp.ClientSession() as session:
                params = {"from": from_city, "to": to_city}
                async with session.get(f"{self.eq12_api_base}/api/deal", params=params) as response:
                    if response.status != 200:
                        await ctx.send("❌ Failed to find travel deal")
                        return

                    deal_data = await response.json()

            # Create Discord message
            message = BotMessage(
                title=f"✈️ {from_city} → {to_city} Deal Alert",
                content=deal_data.get("summary", "Found new travel deal"),
                embed_color=0x00D4AA,
                fields=[
                    {
                        "name": "Price",
                        "value": f"${deal_data.get('price', 0)}",
                        "inline": True,
                    },
                    {
                        "name": "Carrier",
                        "value": deal_data.get("carrier", "TBD"),
                        "inline": True,
                    },
                    {
                        "name": "Dates",
                        "value": deal_data.get("dates", "Flexible"),
                        "inline": True,
                    },
                ],
            )

            # Send to travel channels
            await self.send_to_channel(ServerType.OPS, ChannelType.TRAVEL, message)
            await self.send_to_channel(ServerType.COMMUNITY, ChannelType.TRAVEL, message)

            await ctx.send("✅ Deal posted to travel channels")

        except Exception as e:
            self.logger.error(f"Deal command failed: {e}")
            await ctx.send("❌ Error finding deal")

    @commands.command(name="sendtv")
    async def sendtv_command(self, ctx, content_type: str = "parlay"):
        """Send content to Apple TV"""
        self.stats["commands_executed"] += 1

        try:
            # Call Apple TV API
            async with aiohttp.ClientSession() as session:
                payload = {"type": content_type, "source": "discord_bot"}
                async with session.post(
                    f"{self.appletv_api_base}/stream", json=payload
                ) as response:
                    if response.status != 200:
                        await ctx.send("❌ Failed to send to Apple TV")
                        return

            # Post to Apple TV channel
            message = BotMessage(
                title="📺 Sent to Apple TV",
                content=f"Streaming {content_type} content to Apple TV devices",
                embed_color=0x007AFF,
            )

            await self.send_to_channel(ServerType.OPS, ChannelType.APPLETV, message)
            await ctx.send("✅ Content sent to Apple TV")

        except Exception as e:
            self.logger.error(f"SendTV command failed: {e}")
            await ctx.send("❌ Error sending to Apple TV")

    @commands.command(name="snip")
    async def snip_command(self, ctx):
        """Show recent snip watcher activity"""
        self.stats["commands_executed"] += 1

        try:
            # Get snip watcher stats
            snip_folder = EQ12_HOME / "snips"
            recent_snips = list(snip_folder.glob("*.png"))[-5:] if snip_folder.exists() else []

            message = BotMessage(
                title="👁️ Snip Watcher Status",
                content="Monitoring screenshot folder for visual data capture",
                embed_color=0x8E44AD,
                fields=[
                    {
                        "name": "Recent Snips",
                        "value": str(len(recent_snips)),
                        "inline": True,
                    },
                    {"name": "Folder", "value": str(snip_folder), "inline": False},
                ],
            )

            await self.send_to_channel(ServerType.OPS, ChannelType.SNIPS, message)
            await ctx.send("✅ Snip status posted")

        except Exception as e:
            self.logger.error(f"Snip command failed: {e}")
            await ctx.send("❌ Error checking snips")

    @commands.command(name="cookbook")
    async def cookbook_command(self, ctx, keyword: str | None = None, *flags):
        """Query EQ12 cookbook patterns and recipes with GPT-5 developer controls"""
        self.stats["commands_executed"] += 1

        # Strict channel restriction with auto-delete
        allowed_channels = ["eq12-dev", "cookbook", "eq12-cookbook", "bot-commands"]
        if ctx.channel.name not in allowed_channels:
            try:
                await ctx.message.delete()  # Auto-delete invalid usage
                # Send ephemeral DM to user about restriction
                try:
                    await ctx.author.send(
                        f"📚 **EQ12 Cookbook Restricted**\n"
                        f"The `!cookbook` command only works in: {', '.join([f'#{ch}' for ch in allowed_channels])}\n"
                        f"This keeps dev recipes organized and prevents channel clutter."
                    )
                except:
                    pass  # User has DMs disabled
            except discord.Forbidden:
                await ctx.send(
                    f"📚 **Channel Restriction**: `!cookbook` only works in {', '.join([f'#{ch}' for ch in allowed_channels])}\n"
                    f"*Note: I need 'Manage Messages' permission to auto-clean invalid usage.*",
                    delete_after=10,
                )
            return

        # Load cookbook configuration
        config_file = EQ12_HOME / "configs" / "cookbook_config.json"
        try:
            with open(config_file) as f:
                config = json.load(f)["cookbook_config"]
            defaults = config.get("platform_overrides", {}).get(
                "discord", config["default_settings"]
            )
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            defaults = {
                "verbosity": "high",
                "reasoning": "medium",
                "grammar": None,
                "freeform": False,
            }

        # Parse GPT-5 developer control flags
        flag_dict = {f.split("=")[0]: f.split("=")[1] for f in flags if "=" in f}
        verbosity = flag_dict.get("verbosity", defaults["verbosity"])
        reasoning = flag_dict.get("reasoning", defaults["reasoning"])
        cfg_grammar = flag_dict.get("grammar", defaults["grammar"])
        freeform = flag_dict.get("freeform", str(defaults["freeform"]).lower()).lower() == "true"

        # Security check for freeform
        if freeform and config.get("security_settings", {}).get("require_auth_for_freeform", True):
            # Check if user has admin role (implement your role logic here)
            admin_roles = ["Admin", "Developer", "EQ12-Admin"]
            user_roles = [role.name for role in ctx.author.roles]
            if not any(role in admin_roles for role in user_roles):
                embed = discord.Embed(
                    title="❌ Access Denied",
                    description="Freeform execution requires admin privileges",
                    color=0xE74C3C,
                )
                embed.add_field(name="Required Roles", value=", ".join(admin_roles), inline=False)
                await ctx.send(embed=embed)
                return

        if not keyword:
            # Show available grammars from config
            available_grammars = list(config.get("grammar_definitions", {}).keys())[
                :6
            ]  # Limit for embed
            grammar_list = ", ".join(available_grammars)

            embed = discord.Embed(
                title="📚 EQ12 Cookbook Query with GPT-5 + CFG Controls",
                description="Query EQ12 patterns with AI controls and grammar enforcement",
                color=0x3498DB,
            )
            embed.add_field(name="Usage", value="`!cookbook <keyword> [flags...]`", inline=False)
            embed.add_field(
                name="Enhanced Examples",
                value=(
                    "• `!cookbook sql grammar=postgres` - PostgreSQL-only SQL\n"
                    "• `!cookbook wireguard grammar=wireguard` - Valid configs\n"
                    "• `!cookbook python grammar=python verbosity=high` - Detailed\n"
                    "• `!cookbook timestamp grammar=regex_timestamp` - ISO format\n"
                    "• `!cookbook fastapi reasoning=minimal` - Ultra-fast"
                ),
                inline=False,
            )
            embed.add_field(
                name="Available CFG Grammars",
                value=grammar_list if grammar_list else "None configured",
                inline=False,
            )
            embed.add_field(
                name="Current Defaults",
                value=f"verbosity={defaults['verbosity']}, reasoning={defaults['reasoning']}",
                inline=True,
            )
            embed.add_field(
                name="GPT-5 Developer Controls",
                value=(
                    "**verbosity=** low|medium|high\n"
                    "**reasoning=** minimal|medium|high\n"
                    "**grammar=** postgres|python|bash|etc\n"
                    "**freeform=** true|false (direct execution)"
                ),
                inline=False,
            )
            embed.add_field(
                name="Available Sections",
                value="Python, PowerShell, Bash, C#, DevOps, AI/GPT, Security, Data, Media, Commerce, Testing",
                inline=False,
            )
            await ctx.send(embed=embed)
            return

        try:
            # Import cookbook query functionality
            import sys

            sys.path.insert(0, str(EQ12_HOME))
            from eq12_cookbook_query import EQ12CookbookQuery

            cookbook = EQ12CookbookQuery()

            # Apply CFG grammar constraints if specified
            grammar_constraint = None
            if cfg_grammar and cfg_grammar in config.get("grammar_definitions", {}):
                grammar_def = config["grammar_definitions"][cfg_grammar]

                # Security check for blocked patterns
                blocked_patterns = config.get("security_settings", {}).get("blocked_patterns", [])
                if any(pattern.upper() in keyword.upper() for pattern in blocked_patterns):
                    embed = discord.Embed(
                        title="❌ Security Restriction",
                        description="Query contains blocked pattern",
                        color=0xE74C3C,
                    )
                    embed.add_field(
                        name="Blocked Patterns",
                        value=", ".join(blocked_patterns),
                        inline=False,
                    )
                    await ctx.send(embed=embed)
                    return

                grammar_constraint = {
                    "type": "grammar",
                    "syntax": grammar_def["syntax"],
                    "definition": grammar_def["definition"],
                    "description": grammar_def["description"],
                }

            # Apply GPT-5 developer controls to search
            if keyword.lower() in ["list", "sections", "help"]:
                embed = discord.Embed(title="📚 EQ12 Cookbook Sections", color=0x2ECC71)
                sections = [
                    "🐍 **python** - Bots & Automation",
                    "🪟 **powershell** - Windows Scripts",
                    "🐧 **bash** - Linux/Shell",
                    "⚙️ **c#** - .NET Development",
                    "🚀 **devops** - CI/CD & GitHub",
                    "🤖 **prompts** - AI/GPT Integration",
                    "🔒 **security** - VPN & Networking",
                    "📊 **data** - Analysis & Databases",
                    "🎬 **media** - Content Generation",
                    "💰 **marketplace** - Commerce",
                    "🧪 **testing** - QA & Testing",
                ]

                embed.description = "\\n".join(sections)
                embed.add_field(
                    name="Usage",
                    value="`!cookbook <section>` or `!cookbook <keyword>`",
                    inline=False,
                )
                await ctx.send(embed=embed)
                return

            # Perform search
            matches = cookbook.keyword_search(keyword)

            if not matches:
                embed = discord.Embed(
                    title="❌ No Results Found",
                    description=f"No matches found for '{keyword}'",
                    color=0xE74C3C,
                )
                embed.add_field(
                    name="Suggestion",
                    value="Try `!cookbook list` to see available sections",
                    inline=False,
                )
                await ctx.send(embed=embed)
                return

            # Apply grammar filtering if specified
            if grammar_constraint:
                section_mappings = config.get("section_grammar_mappings", {})
                relevant_sections = []
                for section, grammars in section_mappings.items():
                    if cfg_grammar in grammars:
                        relevant_sections.append(section)

                if relevant_sections:
                    matches = [
                        m
                        for m in matches
                        if any(section in m["section"].lower() for section in relevant_sections)
                    ]

            # Format results for Discord with GPT-5 + CFG control indicators
            control_summary = []
            if verbosity != defaults["verbosity"]:
                control_summary.append(f"verbosity={verbosity}")
            if reasoning != defaults["reasoning"]:
                control_summary.append(f"reasoning={reasoning}")
            if cfg_grammar:
                control_summary.append(f"CFG={cfg_grammar}")
            if freeform:
                control_summary.append("freeform=enabled")

            title = f"🔍 Cookbook Results: {keyword}"
            if control_summary:
                title += f" [{', '.join(control_summary)}]"

            description = f"Found {len(matches)} matches"
            if grammar_constraint:
                description += f"\n📜 **CFG Enforced:** {grammar_constraint['description']}"

            embed = discord.Embed(title=title, description=description, color=0x3498DB)

            current_section = None
            field_content = []
            field_count = 0
            max_fields = 10  # Discord embed limit

            for match in matches[:15]:  # Limit to 15 results
                if field_count >= max_fields:
                    break

                section = match["section"].replace("_", " ").title()

                if section != current_section:
                    if field_content and current_section:
                        # Add previous section's content
                        embed.add_field(
                            name=f"📍 {current_section}",
                            value="\\n".join(field_content),
                            inline=False,
                        )
                        field_count += 1
                        field_content = []

                    current_section = section

                # Format the match line
                line = match["line"].strip()
                if len(line) > 80:
                    line = line[:77] + "..."

                # Add appropriate emoji and formatting
                if match["type"] == "code":
                    field_content.append(f"💻 `{line}`")
                else:
                    field_content.append(f"📝 {line}")

                if len(field_content) >= 3:  # Max 3 items per section to avoid clutter
                    break

            # Add final section
            if field_content and current_section and field_count < max_fields:
                embed.add_field(
                    name=f"📍 {current_section}",
                    value="\\n".join(field_content),
                    inline=False,
                )

            # Add footer with GPT-5 control info
            footer_text = f"GPT-5 Controls: verbosity={verbosity}, reasoning={reasoning}"
            if cfg_grammar:
                footer_text += f", grammar={cfg_grammar}"
            if freeform:
                footer_text += ", freeform=enabled"
            embed.set_footer(text=footer_text)

            await ctx.send(embed=embed)

            # Log successful query with GPT-5 controls
            control_log = (
                ", ".join([f"{k}={v}" for k, v in flag_dict.items()]) if flag_dict else "default"
            )
            message = BotMessage(
                title="📚 Cookbook Query with GPT-5 Controls",
                content=f"User {ctx.author} queried: {keyword}",
                embed_color=0x3498DB,
                fields=[
                    {"name": "Results", "value": str(len(matches)), "inline": True},
                    {"name": "Channel", "value": ctx.channel.name, "inline": True},
                    {"name": "GPT-5 Controls", "value": control_log, "inline": False},
                ],
            )
            await self.send_to_channel(ServerType.OPS, ChannelType.LOGS, message)

        except ImportError as e:
            embed = discord.Embed(
                title="❌ Cookbook Module Error",
                description="Cookbook query system not available",
                color=0xE74C3C,
            )
            embed.add_field(name="Error", value=f"`{e!s}`", inline=False)
            embed.add_field(
                name="Path",
                value=f"Make sure `eq12_cookbook_query.py` is in `{EQ12_HOME}`",
                inline=False,
            )
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Cookbook command error: {e}")
            embed = discord.Embed(
                title="❌ Cookbook Error",
                description="An error occurred while querying the cookbook",
                color=0xE74C3C,
            )
            embed.add_field(name="Error", value=str(e), inline=False)
            embed.add_field(
                name="Suggestion",
                value="Try `!cookbook list` or contact admin",
                inline=False,
            )
            await ctx.send(embed=embed)

    # === BACKGROUND TASKS ===

    @tasks.loop(minutes=15)
    async def sync_with_telegram(self):
        """Sync with Telegram bot periodically"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.telegram_api_base}/status") as response:
                    if response.status == 200:
                        telegram_data = await response.json()
                        self.logger.debug(f"Telegram sync: {telegram_data}")
                    else:
                        self.logger.warning(f"Telegram sync failed: {response.status}")

        except Exception as e:
            self.logger.error(f"Telegram sync error: {e}")

    @tasks.loop(minutes=30)
    async def monitor_eq12_apis(self):
        """Monitor EQ12 API health"""
        try:
            apis = [
                ("EQ12 API", self.eq12_api_base),
                ("Apple TV API", self.appletv_api_base),
                ("Telegram API", self.telegram_api_base),
            ]

            status_updates = []

            async with aiohttp.ClientSession() as session:
                for name, url in apis:
                    try:
                        async with session.get(f"{url}/health", timeout=10) as response:
                            status = (
                                "✅ Online"
                                if response.status == 200
                                else f"❌ Error ({response.status})"
                            )
                    except Exception:
                        status = "🔴 Offline"

                    status_updates.append(f"**{name}**: {status}")

            # Send to logs channel
            if status_updates and ServerType.OPS in self.servers:
                message = BotMessage(
                    title="🔧 API Health Check",
                    content="\n".join(status_updates),
                    embed_color=0x95A5A6,
                )

                await self.send_to_channel(
                    ServerType.OPS, ChannelType.LOGS, message, cross_post=False
                )

        except Exception as e:
            self.logger.error(f"API monitor error: {e}")


async def main():
    """Main entry point"""
    if not DISCORD_AVAILABLE:
        print("ERROR: Missing Discord dependencies")
        print("Install with: pip install discord.py aiohttp")
        return

    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    if not bot_token:
        print("ERROR: DISCORD_BOT_TOKEN environment variable not set")
        return

    bot = EQ12DiscordBot()

    try:
        await bot.start(bot_token)
    except KeyboardInterrupt:
        bot.logger.info("Shutting down EQ12 Discord Bot...")
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
