package main

import (
	"fmt"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestViperConfig(t *testing.T) {
	fakeURI := "fake_uri"
	os.Setenv("MONGODB_URI", fakeURI)
	fakeSandbox := "fake_sandbox"
	os.Setenv("BACKEND_SANDBOX_ROOT", fakeSandbox)
	fakeHostPort := 1001
	os.Setenv("VIEWER_HOST_PORT", fmt.Sprintf("%d", fakeHostPort))

	config := InitViperConfig()
	assert.Equal(t, fakeURI, config.MongoDBURI)
	assert.Equal(t, fakeSandbox, config.YmirSandbox)
	assert.Equal(t, fakeHostPort, config.ViewerPort)
}
