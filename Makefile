# Determine the current platform
ifeq ($(OS),Windows_NT)
	CURRENT_PLATFORM = windows
	RM_CMD = del /s /q
	RMDIR_CMD = rmdir /s /q
	SLASH = "\"
	INSTALL = python3 -m PyInstaller
	MD = mkdir
	EXE = main.exe
	CP = copy
else
	UNAME := $(shell uname -s)
	ifeq ($(UNAME),Linux)
		CURRENT_PLATFORM = linux
		RM_CMD = rm -rf
		RMDIR_CMD = rm -rf
		SLASH = "/"
		INSTALL = pyinstaller
		MD = mkdir -p
		EXE = main
		CP = cp
	else
		$(error Unsupported platform: $(UNAME))
	endif
endif


# Define the release directory and platform subdirectory
RELEASE_DIR = release
PLATFORM_DIR = "$(RELEASE_DIR)$(SLASH)$(CURRENT_PLATFORM)"

all: create_dirs build

create_dirs:
	@$(MD) "$(PLATFORM_DIR)"

build:
	@$(INSTALL) --onefile --paths ./ --hidden-import common --hidden-import stock_data --hidden-import twitter main.py
	@$(CP) "dist$(SLASH)$(EXE)" "$(PLATFORM_DIR)"
	@$(RM_CMD) main.spec
	@$(RMDIR_CMD) build dist

clean:
	@$(RMDIR_CMD) $(RELEASE_DIR)

.PHONY: all create_dirs build clean
