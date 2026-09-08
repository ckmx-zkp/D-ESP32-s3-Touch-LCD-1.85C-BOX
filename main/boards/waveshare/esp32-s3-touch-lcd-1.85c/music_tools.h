#pragma once

#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include "application.h"
#include "mcp_server.h"

inline void RegisterPrivateMusicTools(McpServer& server) {
    server.AddTool(
        "self.music.play_url",
        "Play a NetEase song returned by search_netease_music. Call only after that search "
        "succeeds, using its exact audio_url, title and artist. Playback starts after the "
        "current spoken response finishes. A new song replaces the previous request.",
        PropertyList({Property("audio_url", kPropertyTypeString),
                      Property("title", kPropertyTypeString, std::string("")),
                      Property("artist", kPropertyTypeString, std::string(""))}),
        [](const PropertyList& properties) -> ReturnValue {
            const auto audio_url = properties["audio_url"].value<std::string>();
            const auto title = properties["title"].value<std::string>();
            const auto artist = properties["artist"].value<std::string>();
            constexpr std::string_view kPrefix =
                "http://47.108.114.17:8081/xiaozhi-music/audio_ogg/";
            if (audio_url.size() <= kPrefix.size() || audio_url.size() > 768 ||
                audio_url.compare(0, kPrefix.size(), kPrefix) != 0 ||
                audio_url.find_first_not_of(
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.",
                    kPrefix.size()) != std::string::npos) {
                throw std::runtime_error("Rejected untrusted music URL");
            }
            if (title.size() > 256 || artist.size() > 256) {
                throw std::runtime_error("Music metadata exceeds 256 bytes");
            }
            std::string text = title;
            if (!artist.empty()) {
                text += text.empty() ? artist : " - " + artist;
            }
            std::vector<NotifySubtitle> subtitles;
            if (!text.empty()) {
                subtitles.push_back({.start_ms = 0, .text = std::move(text)});
            }
            Application::GetInstance().QueueNotification(audio_url, std::move(subtitles));
            return std::string("Music queued; playback starts after the spoken response finishes.");
        });
    server.AddTool("self.music.stop", "Stop NetEase music playback and cancel any queued song.",
                   PropertyList(), [](const PropertyList&) -> ReturnValue {
                       Application::GetInstance().CancelNotificationPlayback();
                       return true;
                   });
}
