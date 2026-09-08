#pragma once

#include "display/lcd_display.h"
#include "lvgl_theme.h"

#include <cstring>

extern const uint8_t box_upgrade_thinking_start[] asm("_binary_box_upgrade_thinking_start");
extern const uint8_t box_upgrade_thinking_end[] asm("_binary_box_upgrade_thinking_end");

class PortraitLcdDisplay : public SpiLcdDisplay {
public:
    using SpiLcdDisplay::SpiLcdDisplay;

    void SetupUI() override {
        if (IsSetupUICalled()) {
            return;
        }
        SpiLcdDisplay::SetupUI();
        ApplyPortraitLayout();
        DisplayLockGuard lock(this);
        lv_obj_add_flag(emoji_label_, LV_OBJ_FLAG_HIDDEN);
        ESP_LOGI("PortraitDisplay", "Full-screen portrait layout: %dx%d", width_, height_);
    }

    void SetTheme(Theme* theme) override {
        SpiLcdDisplay::SetTheme(theme);
        ApplyPortraitLayout();
    }

    void SetEmotion(const char* emotion) override {
        if (!IsSetupUICalled() || emotion == nullptr) {
            return;
        }
        if (strcmp(emotion, "download") == 0 || strcmp(emotion, "cloud_download") == 0) {
            DisplayLockGuard lock(this);
            // Resources are not applied yet during boot-time assets updates. Keep this
            // PNG in the application partition so it also survives assets unmapping.
            if (gif_controller_) {
                gif_controller_->Stop();
                gif_controller_.reset();
            }
            lv_image_set_src(emoji_image_, upgrade_thinking_.image_dsc());
            lv_obj_add_flag(emoji_label_, LV_OBJ_FLAG_HIDDEN);
            lv_obj_remove_flag(emoji_image_, LV_OBJ_FLAG_HIDDEN);
            ESP_LOGI("PortraitDisplay", "Built-in thinking background: %s", emotion);
            return;
        }
        // System-status symbols share the same portrait vocabulary as cloud emotions.
        const char* portrait = emotion;
        if (strcmp(emotion, "robot_2") == 0 || strcmp(emotion, "link") == 0) {
            portrait = "neutral";
        } else if (strcmp(emotion, "warning") == 0 || strcmp(emotion, "cloud_off") == 0) {
            portrait = "confused";
        } else if (strcmp(emotion, "cancel") == 0) {
            portrait = "sad";
        }
        auto collection = static_cast<LvglTheme*>(current_theme_)->emoji_collection();
        if (collection == nullptr) {
            return;
        }
        if (collection->GetEmojiImage(portrait) == nullptr) {
            portrait = "neutral";
        }
        if (collection->GetEmojiImage(portrait) == nullptr) {
            ESP_LOGE("PortraitDisplay", "Portrait assets are missing");
            return;
        }
        SpiLcdDisplay::SetEmotion(portrait);
        ESP_LOGI("PortraitDisplay", "Emotion %s -> %s", emotion, portrait);
    }

private:
    LvglRawImage upgrade_thinking_{
        const_cast<uint8_t*>(box_upgrade_thinking_start),
        static_cast<size_t>(box_upgrade_thinking_end - box_upgrade_thinking_start)};

    void ApplyPortraitLayout() {
        if (!IsSetupUICalled()) {
            return;
        }
        DisplayLockGuard lock(this);
        auto theme = static_cast<LvglTheme*>(current_theme_);
        const int text_height = theme->text_font()->font()->line_height;
        const int icon_height = theme->icon_font()->font()->line_height;
        lv_obj_set_size(emoji_box_, width_, height_);
        lv_obj_set_style_radius(emoji_box_, 0, 0);
        lv_obj_remove_flag(emoji_box_, LV_OBJ_FLAG_SCROLLABLE);
        lv_obj_center(emoji_box_);
        lv_obj_center(emoji_image_);
        lv_obj_set_style_bg_color(container_, lv_color_white(), 0);
        lv_obj_set_style_bg_color(lv_screen_active(), lv_color_white(), 0);

        // Narrow overlays stay inside the circular panel and away from eyes and mouth.
        lv_obj_set_size(status_bar_, 110, text_height + 2);
        lv_obj_set_style_pad_all(status_bar_, 0, 0);
        lv_obj_align(status_bar_, LV_ALIGN_TOP_MID, 0, 4);
        lv_obj_set_width(status_label_, 100);
        lv_obj_set_width(notification_label_, 100);
        lv_label_set_long_mode(notification_label_, LV_LABEL_LONG_SCROLL_CIRCULAR);

        lv_obj_set_size(top_bar_, 216, icon_height + 4);
        lv_obj_set_style_pad_all(top_bar_, 0, 0);
        lv_obj_set_style_bg_opa(top_bar_, LV_OPA_TRANSP, 0);
        lv_obj_align(top_bar_, LV_ALIGN_BOTTOM_MID, 0, -58);

        lv_obj_set_size(bottom_bar_, 192, text_height + 4);
        lv_obj_set_style_pad_all(bottom_bar_, 0, 0);
        lv_obj_set_style_bg_color(bottom_bar_, lv_color_white(), 0);
        lv_obj_set_style_bg_opa(bottom_bar_, LV_OPA_80, 0);
        lv_obj_align(bottom_bar_, LV_ALIGN_BOTTOM_MID, 0, -26);
        lv_obj_set_width(chat_message_label_, 184);
        lv_label_set_long_mode(chat_message_label_, LV_LABEL_LONG_SCROLL_CIRCULAR);

        for (auto label : {status_label_, notification_label_, network_label_, mute_label_,
                           battery_label_, chat_message_label_}) {
            lv_obj_set_style_text_color(label, lv_color_black(), 0);
        }
    }
};
