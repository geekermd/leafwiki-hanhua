// Package usersettings stores each user's private preferences (language,
// autosave, ...). Like favorites, this data is not derived from the
// filesystem tree and must never be touched by resync (see ADR-0001).
package usersettings

import "time"

// DefaultLanguage is the language assigned to a user who has never set one.
//
// NOTE (leafwiki-zh): upstream ships "en". This Simplified-Chinese build uses
// "zh" so users without a saved preference really get the Chinese UI — the
// frontend applies the per-user value on top of the site-wide
// --default-language, so leaving this at "en" would override it.
const DefaultLanguage = "zh"

// DefaultDateFormat / DefaultTimeFormat mean "follow the active UI language"
// — the value assigned to a user who has never picked an explicit format.
const (
	DefaultDateFormat = "locale"
	DefaultTimeFormat = "locale"
)

// UserSettings holds a single user's preferences.
type UserSettings struct {
	UserID     string    `json:"userId"`
	Language   string    `json:"language"`
	AutoSave   bool      `json:"autoSave"`
	DateFormat string    `json:"dateFormat"`
	TimeFormat string    `json:"timeFormat"`
	UpdatedAt  time.Time `json:"updatedAt"`
}

// DefaultUserSettings returns the settings a user has before ever saving any
// preferences — never persisted by itself, only returned in-memory by Get.
func DefaultUserSettings(userID string) *UserSettings {
	return &UserSettings{
		UserID:     userID,
		Language:   DefaultLanguage,
		AutoSave:   true,
		DateFormat: DefaultDateFormat,
		TimeFormat: DefaultTimeFormat,
	}
}
