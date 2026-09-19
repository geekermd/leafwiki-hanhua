package usersettings

import (
	"reflect"
	"testing"
)

func TestAllowedLanguages_ReturnsSortedShippedCodes(t *testing.T) {
	got := AllowedLanguages()
	// leafwiki-zh: "zh" is shipped by this fork (upstream ships de/en/es only),
	// so keep this list in sync with ui/leafwiki-ui/src/locales/.
	want := []string{"de", "en", "es", "zh"}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("expected %v, got %v", want, got)
	}
}

func TestIsAllowedLanguage_AcceptsShippedCodesAndRejectsUnknownOnes(t *testing.T) {
	for _, lang := range []string{"en", "de", "es", "zh"} {
		if !IsAllowedLanguage(lang) {
			t.Errorf("expected %q to be allowed", lang)
		}
	}
	if IsAllowedLanguage("xx-not-a-real-language") {
		t.Error("expected an unshipped language code to be rejected")
	}
}
