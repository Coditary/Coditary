#!/usr/bin/env python3
"""Generate s/slack.yaml with comprehensive bot-token Web API coverage."""
from __future__ import annotations

from pathlib import Path
from textwrap import indent

HEADER = """name: slack
version: "1.0.0"
description: Slack Web API for workspace messaging, channels, users, and automation
base_url: https://slack.com/api

env:
  - name: SLACK_BOT_TOKEN
    required: true

auth:
  token:
    type: bearer
    token: ${SLACK_BOT_TOKEN}

errors:
  default: "Slack API error (HTTP {status}): {output.error}"
  401: "Authentication failed — check SLACK_BOT_TOKEN (invalid_auth, token_revoked, or account_inactive)"
  403: "Forbidden — your token lacks permission ({output.error}: missing_scope, not_allowed, or not_in_channel)"
  404: "Not found — {output.error} (channel_not_found, user_not_found, or message_not_found)"
  429: "Rate limited — retry after the window shown in response headers"

commands:
"""

# (group, command, method, endpoint, params, form_fields, success_message)
# params: list of (name, description, type, required, enum?)
METHODS: list[tuple] = [
    # auth
    ("auth", "test", "POST", "/auth.test", [], None,
     "Authenticated as {output.user} on team {output.team} ({output.team_id})"),
    # conversations
    ("conversations", "list", "GET", "/conversations.list",
     [("exclude_archived", "Exclude archived channels", "boolean", False, None),
      ("types", "Comma-separated channel types", "string", False, None),
      ("limit", "Maximum channels to return (max 1000)", "number", False, None),
      ("cursor", "Pagination cursor", "string", False, None)],
     None, "Listed workspace channels — use --pretty for the full channel list"),
    ("conversations", "info", "GET", "/conversations.info",
     [("channel", "Conversation ID", "string", True, None),
      ("include_locale", "Include locale", "boolean", False, None),
      ("include_num_members", "Include member count", "boolean", False, None)],
     None, "Channel {output.channel.name} ({output.channel.id})"),
    ("conversations", "history", "GET", "/conversations.history",
     [("channel", "Conversation ID", "string", True, None),
      ("limit", "Maximum messages to return", "number", False, None),
      ("cursor", "Pagination cursor", "string", False, None),
      ("latest", "End of time range (message ts)", "string", False, None),
      ("oldest", "Start of time range (message ts)", "string", False, None),
      ("inclusive", "Include messages with latest or oldest ts", "boolean", False, None)],
     None, "Fetched message history for {input.channel}"),
    ("conversations", "replies", "GET", "/conversations.replies",
     [("channel", "Conversation ID", "string", True, None),
      ("ts", "Parent message timestamp", "string", True, None),
      ("limit", "Maximum messages to return", "number", False, None),
      ("cursor", "Pagination cursor", "string", False, None)],
     None, "Fetched thread replies for message {input.ts}"),
    ("conversations", "members", "GET", "/conversations.members",
     [("channel", "Conversation ID", "string", True, None),
      ("limit", "Maximum members to return", "number", False, None),
      ("cursor", "Pagination cursor", "string", False, None)],
     None, "Listed members of {input.channel}"),
    ("conversations", "create", "POST", "/conversations.create",
     [("name", "Channel name", "string", True, None),
      ("is_private", "Create a private channel", "boolean", False, None),
      ("team_id", "Workspace ID where the channel is created", "string", False, None)],
     ["name", "is_private", "team_id"], "Created channel {output.channel.name} ({output.channel.id})"),
    ("conversations", "invite", "POST", "/conversations.invite",
     [("channel", "Conversation ID", "string", True, None),
      ("users", "Comma-separated user IDs to invite", "string", True, None)],
     ["channel", "users"], "Invited users to {input.channel}"),
    ("conversations", "join", "POST", "/conversations.join",
     [("channel", "Conversation ID or name", "string", True, None)],
     ["channel"], "Joined channel {output.channel.name} ({output.channel.id})"),
    ("conversations", "open", "POST", "/conversations.open",
     [("channel", "Conversation ID to reopen", "string", False, None),
      ("users", "Comma-separated user IDs for a DM", "string", False, None),
      ("return_im", "Return IM channel metadata", "boolean", False, None)],
     ["channel", "users", "return_im"], "Opened conversation {output.channel.id}"),
    ("conversations", "archive", "POST", "/conversations.archive",
     [("channel", "Conversation ID", "string", True, None)],
     ["channel"], "Archived channel {input.channel}"),
    ("conversations", "unarchive", "POST", "/conversations.unarchive",
     [("channel", "Conversation ID", "string", True, None)],
     ["channel"], "Unarchived channel {input.channel}"),
    ("conversations", "rename", "POST", "/conversations.rename",
     [("channel", "Conversation ID", "string", True, None),
      ("name", "New channel name", "string", True, None)],
     ["channel", "name"], "Renamed channel to {output.channel.name}"),
    ("conversations", "set-topic", "POST", "/conversations.setTopic",
     [("channel", "Conversation ID", "string", True, None),
      ("topic", "New topic string", "string", True, None)],
     ["channel", "topic"], "Updated topic for {input.channel}"),
    ("conversations", "set-purpose", "POST", "/conversations.setPurpose",
     [("channel", "Conversation ID", "string", True, None),
      ("purpose", "New purpose string", "string", True, None)],
     ["channel", "purpose"], "Updated purpose for {input.channel}"),
    ("conversations", "kick", "POST", "/conversations.kick",
     [("channel", "Conversation ID", "string", True, None),
      ("user", "User ID to remove", "string", True, None)],
     ["channel", "user"], "Removed user {input.user} from {input.channel}"),
    ("conversations", "leave", "POST", "/conversations.leave",
     [("channel", "Conversation ID", "string", True, None)],
     ["channel"], "Left channel {input.channel}"),
    ("conversations", "close", "POST", "/conversations.close",
     [("channel", "Conversation ID", "string", True, None)],
     ["channel"], "Closed conversation {input.channel}"),
    ("conversations", "mark", "POST", "/conversations.mark",
     [("channel", "Conversation ID", "string", True, None),
      ("ts", "Message timestamp to mark as read", "string", True, None)],
     ["channel", "ts"], "Marked {input.channel} read through {input.ts}"),
    ("conversations", "canvases-create", "POST", "/conversations.canvases.create",
     [("channel_id", "Channel ID", "string", True, None),
      ("title", "Canvas title", "string", False, None),
      ("document_content", "Initial canvas content", "string", False, None)],
     ["channel_id", "title", "document_content"], "Created canvas in channel {input.channel_id}"),
    # chat
    ("chat", "post-message", "POST", "/chat.postMessage",
     [("channel", "Channel ID or name", "string", True, None),
      ("text", "Message text", "string", True, None),
      ("thread_ts", "Parent message timestamp for thread reply", "string", False, None),
      ("reply_broadcast", "Also post thread reply to channel", "boolean", False, None),
      ("unfurl_links", "Enable link unfurling", "boolean", False, None),
      ("unfurl_media", "Enable media unfurling", "boolean", False, None)],
     ["channel", "text", "thread_ts", "reply_broadcast", "unfurl_links", "unfurl_media"],
     "Posted message to {input.channel} (ts {output.ts})"),
    ("chat", "update", "POST", "/chat.update",
     [("channel", "Channel ID", "string", True, None),
      ("ts", "Message timestamp to update", "string", True, None),
      ("text", "Updated message text", "string", True, None),
      ("link_names", "Find and link channel names and usernames", "boolean", False, None)],
     ["channel", "ts", "text", "link_names"], "Updated message {input.ts} in {input.channel}"),
    ("chat", "delete", "POST", "/chat.delete",
     [("channel", "Channel ID", "string", True, None),
      ("ts", "Message timestamp to delete", "string", True, None)],
     ["channel", "ts"], "Deleted message {input.ts} from {input.channel}"),
    ("chat", "post-ephemeral", "POST", "/chat.postEphemeral",
     [("channel", "Channel ID", "string", True, None),
      ("user", "User ID who will see the message", "string", True, None),
      ("text", "Message text", "string", True, None),
      ("thread_ts", "Parent message timestamp", "string", False, None)],
     ["channel", "user", "text", "thread_ts"], "Posted ephemeral message to {input.user} in {input.channel}"),
    ("chat", "schedule-message", "POST", "/chat.scheduleMessage",
     [("channel", "Channel ID", "string", True, None),
      ("text", "Message text", "string", True, None),
      ("post_at", "Unix timestamp when to post", "number", True, None),
      ("thread_ts", "Parent message timestamp", "string", False, None)],
     ["channel", "text", "post_at", "thread_ts"], "Scheduled message for {input.channel} at {input.post_at}"),
    ("chat", "delete-scheduled-message", "POST", "/chat.deleteScheduledMessage",
     [("channel", "Channel ID", "string", True, None),
      ("scheduled_message_id", "Scheduled message ID", "string", True, None)],
     ["channel", "scheduled_message_id"], "Deleted scheduled message {input.scheduled_message_id}"),
    ("chat", "me-message", "POST", "/chat.meMessage",
     [("channel", "Channel ID", "string", True, None),
      ("text", "/me message text", "string", True, None)],
     ["channel", "text"], "Posted /me message to {input.channel}"),
    ("chat", "unfurl", "POST", "/chat.unfurl",
     [("channel", "Channel ID", "string", True, None),
      ("ts", "Message timestamp containing the link", "string", True, None),
      ("unfurls", "JSON-encoded unfurl metadata", "string", True, None),
      ("user_auth_message", "Auth message for unfurling", "string", False, None)],
     ["channel", "ts", "unfurls", "user_auth_message"], "Unfurled link in message {input.ts}"),
    # users
    ("users", "list", "GET", "/users.list",
     [("limit", "Maximum users to return", "number", False, None),
      ("cursor", "Pagination cursor", "string", False, None),
      ("include_locale", "Include locale for each user", "boolean", False, None)],
     None, "Listed workspace members — use --pretty for the full user list"),
    ("users", "info", "GET", "/users.info",
     [("user", "User ID", "string", True, None),
      ("include_locale", "Include user locale", "boolean", False, None)],
     None, "User {output.user.name} ({output.user.id}) — {output.user.profile.real_name}"),
    ("users", "lookup-by-email", "GET", "/users.lookupByEmail",
     [("email", "Email address", "string", True, None)],
     None, "Found user {output.user.name} ({output.user.id}) for {input.email}"),
    ("users", "profile-get", "GET", "/users.profile.get",
     [("user", "User ID (defaults to authed user)", "string", False, None),
      ("include_labels", "Include custom profile field labels", "boolean", False, None)],
     None, "Profile for user {output.profile.real_name}"),
    ("users", "get-presence", "GET", "/users.getPresence",
     [("user", "User ID", "string", False, None)],
     None, "Presence for {input.user}: {output.presence}"),
    ("users", "set-presence", "POST", "/users.setPresence",
     [("presence", "Presence value (auto or away)", "string", True, ["auto", "away"])],
     ["presence"], "Set presence to {input.presence}"),
    ("users", "conversations", "GET", "/users.conversations",
     [("user", "User ID", "string", False, None),
      ("types", "Comma-separated channel types", "string", False, None),
      ("exclude_archived", "Exclude archived channels", "boolean", False, None),
      ("limit", "Maximum channels to return", "number", False, None),
      ("cursor", "Pagination cursor", "string", False, None)],
     None, "Listed conversations for user"),
    # bots
    ("bots", "info", "GET", "/bots.info",
     [("bot", "Bot user ID", "string", False, None)],
     None, "Bot {output.bot.name} ({output.bot.id})"),
    # files
    ("files", "list", "GET", "/files.list",
     [("channel", "Filter by channel ID", "string", False, None),
      ("user", "Filter by user ID", "string", False, None),
      ("types", "Filter by file types", "string", False, None),
      ("count", "Number of files to return", "number", False, None),
      ("page", "Page number", "number", False, None)],
     None, "Listed files — use --pretty for details"),
    ("files", "info", "GET", "/files.info",
     [("file", "File ID", "string", True, None),
      ("count", "Number of comments to return", "number", False, None),
      ("page", "Comment page number", "number", False, None)],
     None, "File {output.file.name} ({output.file.id})"),
    ("files", "delete", "POST", "/files.delete",
     [("file", "File ID", "string", True, None)],
     ["file"], "Deleted file {input.file}"),
    ("files", "get-upload-url-external", "POST", "/files.getUploadURLExternal",
     [("filename", "Filename including extension", "string", True, None),
      ("length", "File size in bytes", "number", True, None),
      ("alt_txt", "Alt text for the file", "string", False, None),
      ("snippet_type", "Syntax type for snippets", "string", False, None)],
     ["filename", "length", "alt_txt", "snippet_type"], "Upload URL created for {input.filename}"),
    ("files", "complete-upload-external", "POST", "/files.completeUploadExternal",
     [("files", "JSON array of file metadata objects", "string", True, None),
      ("channel_id", "Channel ID to share the file in", "string", False, None),
      ("initial_comment", "Message introducing the file", "string", False, None),
      ("thread_ts", "Thread timestamp", "string", False, None)],
     ["files", "channel_id", "initial_comment", "thread_ts"], "Completed external file upload"),
    ("files", "upload", "POST", "/files.upload",
     [("channels", "Comma-separated channel IDs", "string", False, None),
      ("content", "File contents", "string", False, None),
      ("filename", "Filename", "string", False, None),
      ("filetype", "File type identifier", "string", False, None),
      ("initial_comment", "Introductory message", "string", False, None),
      ("thread_ts", "Thread timestamp", "string", False, None),
      ("title", "Title of file", "string", False, None)],
     ["channels", "content", "filename", "filetype", "initial_comment", "thread_ts", "title"],
     "Uploaded file {output.file.name} ({output.file.id})"),
    # files.remote
    ("files", "remote-add", "POST", "/files.remote.add",
     [("external_id", "Creator-defined GUID", "string", True, None),
      ("external_url", "URL of the remote file", "string", True, None),
      ("title", "Title of the file", "string", True, None),
      ("filetype", "File type", "string", False, None),
      ("indexable_file_contents", "Indexable plain-text content", "string", False, None),
      ("preview_image", "Preview image URL", "string", False, None)],
     ["external_id", "external_url", "title", "filetype", "indexable_file_contents", "preview_image"],
     "Added remote file {output.file.external_id}"),
    ("files", "remote-info", "GET", "/files.remote.info",
     [("file", "File ID", "string", False, None),
      ("external_id", "External ID", "string", False, None)],
     None, "Remote file {output.file.title} ({output.file.id})"),
    ("files", "remote-list", "GET", "/files.remote.list",
     [("channel", "Channel ID filter", "string", False, None),
      ("ts", "Timestamp filter", "string", False, None),
      ("limit", "Maximum files to return", "number", False, None),
      ("cursor", "Pagination cursor", "string", False, None)],
     None, "Listed remote files"),
    ("files", "remote-remove", "POST", "/files.remote.remove",
     [("file", "File ID", "string", False, None),
      ("external_id", "External ID", "string", False, None)],
     ["file", "external_id"], "Removed remote file"),
    # reactions
    ("reactions", "add", "POST", "/reactions.add",
     [("channel", "Channel ID", "string", True, None),
      ("name", "Emoji name without colons", "string", True, None),
      ("timestamp", "Message timestamp", "string", True, None)],
     ["channel", "name", "timestamp"], "Added :{input.name}: reaction to {input.timestamp}"),
    ("reactions", "get", "GET", "/reactions.get",
     [("channel", "Channel ID", "string", False, None),
      ("timestamp", "Message timestamp", "string", False, None),
      ("file", "File ID", "string", False, None),
      ("file_comment", "File comment ID", "string", False, None),
      ("full", "Return full message payload", "boolean", False, None)],
     None, "Fetched reactions"),
    ("reactions", "remove", "POST", "/reactions.remove",
     [("channel", "Channel ID", "string", False, None),
      ("name", "Emoji name without colons", "string", True, None),
      ("timestamp", "Message timestamp", "string", False, None),
      ("file", "File ID", "string", False, None),
      ("file_comment", "File comment ID", "string", False, None)],
     ["channel", "name", "timestamp", "file", "file_comment"], "Removed :{input.name}: reaction"),
    ("reactions", "list", "GET", "/reactions.list",
     [("user", "User ID", "string", False, None),
      ("full", "Return full message payloads", "boolean", False, None),
      ("count", "Items per page", "number", False, None),
      ("page", "Page number", "number", False, None),
      ("cursor", "Pagination cursor", "string", False, None)],
     None, "Listed reactions"),
    # team
    ("team", "info", "GET", "/team.info",
     [("team", "Team ID to look up", "string", False, None)],
     None, "Workspace {output.team.name} ({output.team.id}) — {output.team.domain}.slack.com"),
    # usergroups
    ("usergroups", "list", "GET", "/usergroups.list",
     [("include_disabled", "Include disabled groups", "boolean", False, None),
      ("include_count", "Include user count", "boolean", False, None),
      ("include_users", "Include member user IDs", "boolean", False, None)],
     None, "Listed user groups"),
    ("usergroups", "create", "POST", "/usergroups.create",
     [("name", "User group handle", "string", True, None),
      ("description", "Short description", "string", False, None),
      ("handle", "Mention handle", "string", False, None),
      ("include_count", "Include user count in response", "boolean", False, None),
      ("channels", "Comma-separated default channel IDs", "string", False, None)],
     ["name", "description", "handle", "include_count", "channels"],
     "Created user group {output.usergroup.name} ({output.usergroup.id})"),
    ("usergroups", "update", "POST", "/usergroups.update",
     [("usergroup", "User group ID", "string", True, None),
      ("name", "New name", "string", False, None),
      ("description", "New description", "string", False, None),
      ("handle", "New mention handle", "string", False, None),
      ("channels", "Comma-separated default channel IDs", "string", False, None),
      ("include_count", "Include user count", "boolean", False, None)],
     ["usergroup", "name", "description", "handle", "channels", "include_count"],
     "Updated user group {output.usergroup.name}"),
    ("usergroups", "enable", "POST", "/usergroups.enable",
     [("usergroup", "User group ID", "string", True, None),
      ("include_count", "Include user count", "boolean", False, None)],
     ["usergroup", "include_count"], "Enabled user group {input.usergroup}"),
    ("usergroups", "disable", "POST", "/usergroups.disable",
     [("usergroup", "User group ID", "string", True, None),
      ("include_count", "Include user count", "boolean", False, None)],
     ["usergroup", "include_count"], "Disabled user group {input.usergroup}"),
    ("usergroups", "users-list", "GET", "/usergroups.users.list",
     [("usergroup", "User group ID", "string", True, None),
      ("include_disabled", "Include disabled users", "boolean", False, None)],
     None, "Listed members of user group {input.usergroup}"),
    ("usergroups", "users-update", "POST", "/usergroups.users.update",
     [("usergroup", "User group ID", "string", True, None),
      ("users", "Comma-separated user IDs", "string", True, None),
      ("include_count", "Include user count", "boolean", False, None)],
     ["usergroup", "users", "include_count"], "Updated members of user group {input.usergroup}"),
    # bookmarks
    ("bookmarks", "list", "POST", "/bookmarks.list",
     [("channel_id", "Channel ID", "string", True, None)],
     ["channel_id"], "Listed bookmarks in {input.channel_id}"),
    ("bookmarks", "add", "POST", "/bookmarks.add",
     [("channel_id", "Channel ID", "string", True, None),
      ("title", "Bookmark title", "string", True, None),
      ("type", "Bookmark type (link)", "string", True, None),
      ("link", "URL for link bookmarks", "string", False, None),
      ("emoji", "Emoji for the bookmark", "string", False, None),
      ("entity_id", "Entity ID for entity bookmarks", "string", False, None)],
     ["channel_id", "title", "type", "link", "emoji", "entity_id"],
     "Added bookmark {input.title} to {input.channel_id}"),
    ("bookmarks", "edit", "POST", "/bookmarks.edit",
     [("channel_id", "Channel ID", "string", True, None),
      ("bookmark_id", "Bookmark ID", "string", True, None),
      ("title", "Updated title", "string", False, None),
      ("link", "Updated URL", "string", False, None),
      ("emoji", "Updated emoji", "string", False, None)],
     ["channel_id", "bookmark_id", "title", "link", "emoji"], "Updated bookmark {input.bookmark_id}"),
    ("bookmarks", "remove", "POST", "/bookmarks.remove",
     [("channel_id", "Channel ID", "string", True, None),
      ("bookmark_id", "Bookmark ID", "string", True, None)],
     ["channel_id", "bookmark_id"], "Removed bookmark {input.bookmark_id}"),
    # pins
    ("pins", "add", "POST", "/pins.add",
     [("channel", "Channel ID", "string", True, None),
      ("timestamp", "Message timestamp to pin", "string", True, None)],
     ["channel", "timestamp"], "Pinned message {input.timestamp} in {input.channel}"),
    ("pins", "list", "GET", "/pins.list",
     [("channel", "Channel ID", "string", True, None)],
     None, "Listed pinned items in {input.channel}"),
    ("pins", "remove", "POST", "/pins.remove",
     [("channel", "Channel ID", "string", True, None),
      ("timestamp", "Message timestamp to unpin", "string", True, None)],
     ["channel", "timestamp"], "Unpinned message {input.timestamp} from {input.channel}"),
    # emoji
    ("emoji", "list", "GET", "/emoji.list", [], None, "Listed custom emoji"),
    # dnd
    ("dnd", "info", "GET", "/dnd.info",
     [("user", "User ID", "string", False, None),
      ("team_id", "Team ID", "string", False, None)],
     None, "Do Not Disturb status for user"),
    ("dnd", "team-info", "GET", "/dnd.teamInfo",
     [("team_id", "Team ID", "string", False, None)],
     None, "Team Do Not Disturb settings"),
    # canvases
    ("canvases", "create", "POST", "/canvases.create",
     [("title", "Canvas title", "string", False, None),
      ("document_content", "Initial canvas content", "string", False, None)],
     ["title", "document_content"], "Created canvas {output.canvas_id}"),
    ("canvases", "delete", "POST", "/canvases.delete",
     [("canvas_id", "Canvas ID", "string", True, None)],
     ["canvas_id"], "Deleted canvas {input.canvas_id}"),
    ("canvases", "access-set", "POST", "/canvases.access.set",
     [("canvas_id", "Canvas ID", "string", True, None),
      ("access_level", "Access level (read, write, owner)", "string", True, None),
      ("channel_ids", "Comma-separated channel IDs", "string", False, None),
      ("user_ids", "Comma-separated user IDs", "string", False, None)],
     ["canvas_id", "access_level", "channel_ids", "user_ids"], "Updated canvas access for {input.canvas_id}"),
    ("canvases", "sections-lookup", "POST", "/canvases.sections.lookup",
     [("canvas_id", "Canvas ID", "string", True, None),
      ("criteria", "JSON lookup criteria", "string", True, None)],
     ["canvas_id", "criteria"], "Looked up canvas sections"),
    # assistant
    ("assistant", "threads-set-status", "POST", "/assistant.threads.setStatus",
     [("channel_id", "Channel ID", "string", True, None),
      ("thread_ts", "Thread timestamp", "string", True, None),
      ("status", "Status text", "string", True, None),
      ("loading_messages", "JSON array of loading messages", "string", False, None)],
     ["channel_id", "thread_ts", "status", "loading_messages"], "Set assistant thread status"),
]


def render_param(name: str, desc: str, typ: str, required: bool, enum: list[str] | None) -> str:
    lines = [
        f"          {name}:",
        f"            description: {desc}",
        f"            type: {typ}",
        f"            required: {'true' if required else 'false'}",
    ]
    if enum:
        lines.append("            enum:")
        lines.extend(f"              - {v}" for v in enum)
    return "\n".join(lines)


def render_leaf(cmd: str, method: str, endpoint: str, params, form_fields, success: str) -> str:
    lines = [
        f"      {cmd}:",
        f"        description: Slack {endpoint.lstrip('/').replace('.', ' ')}",
        f"        endpoint: {endpoint}",
        f"        method: {method}",
        "        auth: token",
        "        headers:",
        "          Accept: application/json",
    ]
    if params:
        lines.append("        params:")
        for p in params:
            lines.append(render_param(*p))
    else:
        lines.append("        params: {}")
    if form_fields:
        lines.append("        body:")
        lines.append("          form:")
        for field in form_fields:
            lines.append(f"            {field}: '{{{field}}}'")
    lines.extend([
        "        responses:",
        "          success:",
        f"            message: \"{success}\"",
        "          failure:",
        f"            message: \"Slack request failed — {{output.error}}\"",
    ])
    return "\n".join(lines)


def main() -> None:
    groups: dict[str, list[str]] = {}
    group_desc = {
        "auth": "Authentication and identity",
        "conversations": "Channels and conversations",
        "chat": "Messages",
        "users": "Workspace members",
        "bots": "Bot users",
        "files": "Files and uploads",
        "reactions": "Message reactions",
        "team": "Workspace",
        "usergroups": "User groups",
        "bookmarks": "Channel bookmarks",
        "pins": "Pinned messages",
        "emoji": "Custom emoji",
        "dnd": "Do Not Disturb",
        "canvases": "Slack canvases",
        "assistant": "Slack AI assistant",
    }
    for group, cmd, method, endpoint, params, form, success in METHODS:
        groups.setdefault(group, []).append(render_leaf(cmd, method, endpoint, params, form, success))

    out = [HEADER.rstrip()]
    for group, leaves in groups.items():
        out.append(f"  {group}:")
        out.append(f"    description: {group_desc.get(group, group.title())}")
        out.append("    commands:")
        out.extend(leaves)
    path = Path(__file__).resolve().parents[3] / "plugins" / "ycallr-apis" / "s" / "slack.yaml"
    path.write_text("\n".join(out) + "\n")
    print(f"Wrote {path} ({len(METHODS)} commands)")


if __name__ == "__main__":
    main()
