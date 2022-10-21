package tools

import (
	"testing"
	"time"
)

func TestTimeTrack(t *testing.T) {
	TimeTrack(time.Now(), "test")
}
