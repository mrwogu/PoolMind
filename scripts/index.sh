#!/bin/bash

# PoolMind Scripts Index
# Interactive navigation tool for PoolMind scripts

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Icons
ICON_SETUP="🔧"
ICON_DEPLOY="🚀"
ICON_DEMO="🎮"
ICON_TEST="🧪"
ICON_TOOLS="🛠️"
ICON_SYSTEMD="⚙️"
ICON_DOCS="📚"

show_header() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                          🎱 PoolMind Scripts Index                          ║"
    echo "║                     Interactive Script Navigation Tool                      ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

show_menu() {
    echo -e "${GREEN}Choose a category:${NC}\n"

    echo -e "${ICON_SETUP} ${YELLOW}1)${NC} ${BLUE}Setup & Installation${NC}    - Install and configure PoolMind"
    echo -e "${ICON_DEPLOY} ${YELLOW}2)${NC} ${BLUE}Deployment & Management${NC} - Deploy, update, and monitor"
    echo -e "${ICON_DEMO} ${YELLOW}3)${NC} ${BLUE}Demos & Simulations${NC}     - Test without hardware"
    echo -e "${ICON_TEST} ${YELLOW}4)${NC} ${BLUE}Testing & Debugging${NC}     - Validate and troubleshoot"
    echo -e "${ICON_TOOLS} ${YELLOW}5)${NC} ${BLUE}Tools & Utilities${NC}       - Helper tools and generators"
    echo -e "${ICON_SYSTEMD} ${YELLOW}6)${NC} ${BLUE}System Services${NC}        - Systemd configuration"
    echo -e "${ICON_DOCS} ${YELLOW}7)${NC} ${BLUE}Documentation${NC}           - Guides and references"
    echo ""
    echo -e "${GREEN}Quick Actions:${NC}"
    echo -e "${YELLOW}q)${NC} Quick setup (development)"
    echo -e "${YELLOW}r)${NC} Run PoolMind"
    echo -e "${YELLOW}d)${NC} Demo mode"
    echo -e "${YELLOW}s)${NC} System status"
    echo -e "${YELLOW}h)${NC} Help and documentation"
    echo -e "${YELLOW}x)${NC} Exit"
    echo ""
}

show_setup_menu() {
    echo -e "${GREEN}${ICON_SETUP} Setup & Installation:${NC}\n"
    echo -e "${YELLOW}1)${NC} setup.sh         - Development environment setup"
    echo -e "${YELLOW}2)${NC} setup-pi.sh      - Raspberry Pi production setup"
    echo -e "${YELLOW}3)${NC} run.sh           - Start PoolMind application"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo ""
}

show_deployment_menu() {
    echo -e "${GREEN}${ICON_DEPLOY} Deployment & Management:${NC}\n"
    echo -e "${YELLOW}1)${NC} update.sh           - Manual system update"
    echo -e "${YELLOW}2)${NC} auto-update.sh      - Automatic update script"
    echo -e "${YELLOW}3)${NC} deploy-remote.sh    - Remote deployment tool"
    echo -e "${YELLOW}4)${NC} status.sh           - System status check"
    echo -e "${YELLOW}5)${NC} validate-renovate.sh - CI dependency validation"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo ""
}

show_demo_menu() {
    echo -e "${GREEN}${ICON_DEMO} Demos & Simulations:${NC}\n"
    echo -e "${YELLOW}1)${NC} demo.py             - Main demo (full pipeline)"
    echo -e "${YELLOW}2)${NC} simple_demo.py      - Simplified computer vision demo"
    echo -e "${YELLOW}3)${NC} virtual_table.py    - Virtual table generator"
    echo -e "${YELLOW}4)${NC} full_simulation.py  - Complete game simulation"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo ""
}

show_testing_menu() {
    echo -e "${GREEN}${ICON_TEST} Testing & Debugging:${NC}\n"
    echo -e "${YELLOW}1)${NC} debug_aruco.py      - ArUco marker debugging"
    echo -e "${YELLOW}2)${NC} debug_markers.py    - Marker quality analysis"
    echo -e "${YELLOW}3)${NC} test_aruco.py       - ArUco detection testing"
    echo -e "${YELLOW}4)${NC} test_pure_aruco.py  - Isolated ArUco testing"
    echo -e "${YELLOW}5)${NC} simple_aruco_test.py - Quick ArUco validation"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo ""
}

show_tools_menu() {
    echo -e "${GREEN}${ICON_TOOLS} Tools & Utilities:${NC}\n"
    echo -e "${YELLOW}1)${NC} gen_markers.py      - Generate ArUco markers"
    echo -e "${YELLOW}2)${NC} camera_test.py      - Camera testing and validation"
    echo -e "${YELLOW}3)${NC} inspect_frame.py    - Frame analysis tool"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo ""
}

show_systemd_menu() {
    echo -e "${GREEN}${ICON_SYSTEMD} System Services:${NC}\n"
    echo -e "${YELLOW}1)${NC} poolmind.service        - Main application service"
    echo -e "${YELLOW}2)${NC} poolmind-update.service - Update service"
    echo -e "${YELLOW}3)${NC} poolmind-update.timer   - Update scheduler"
    echo -e "${YELLOW}4)${NC} Install services        - Copy to systemd"
    echo -e "${YELLOW}5)${NC} Service status          - Check service health"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo ""
}

show_docs_menu() {
    echo -e "${GREEN}${ICON_DOCS} Documentation:${NC}\n"
    echo -e "${YELLOW}1)${NC} Main README          - Complete scripts reference"
    echo -e "${YELLOW}2)${NC} QUICKSTART.md        - Quick start guide"
    echo -e "${YELLOW}3)${NC} SIMULATION.md        - Simulation guide"
    echo -e "${YELLOW}4)${NC} Browse documentation - Open documentation folder"
    echo -e "${YELLOW}b)${NC} Back to main menu"
    echo ""
}

run_script() {
    local category=$1
    local script=$2
    local extension=${3:-""}

    local script_path="${category}/${script}${extension}"

    if [[ ! -f "$script_path" ]]; then
        echo -e "${RED}Error: Script not found: $script_path${NC}"
        return 1
    fi

    echo -e "${GREEN}Running: ${script_path}${NC}"
    echo "----------------------------------------"

    if [[ "$extension" == ".py" ]]; then
        # Python script
        if [[ -z "${PYTHONPATH:-}" ]]; then
            export PYTHONPATH="$(pwd)/../src"
        fi
        if [[ ! -d "../.venv" ]]; then
            echo -e "${YELLOW}Warning: Virtual environment not found. Please run setup first.${NC}"
            read -p "Continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                return 1
            fi
        else
            source ../.venv/bin/activate
        fi
        python "$script_path" "$@"
    else
        # Shell script
        chmod +x "$script_path" 2>/dev/null || true
        ./"$script_path" "$@"
    fi
}

quick_setup() {
    echo -e "${GREEN}${ICON_SETUP} Quick Development Setup${NC}"
    echo "This will set up PoolMind for local development..."
    echo ""
    run_script "setup" "setup" ".sh"
}

quick_run() {
    echo -e "${GREEN}${ICON_SETUP} Starting PoolMind${NC}"
    run_script "setup" "run" ".sh"
}

quick_demo() {
    echo -e "${GREEN}${ICON_DEMO} Starting Demo Mode${NC}"
    echo "Running PoolMind demo without camera..."
    echo ""
    run_script "demo" "demo" ".py"
}

quick_status() {
    echo -e "${GREEN}${ICON_DEPLOY} System Status Check${NC}"
    run_script "deployment" "status" ".sh"
}

show_help() {
    echo -e "${GREEN}${ICON_DOCS} PoolMind Scripts Help${NC}\n"
    echo "This interactive tool helps you navigate and run PoolMind scripts."
    echo ""
    echo -e "${BLUE}Directory Structure:${NC}"
    echo "├── setup/       - Installation and configuration scripts"
    echo "├── deployment/  - Deployment and management scripts"
    echo "├── demo/        - Demo and simulation scripts"
    echo "├── testing/     - Testing and debugging scripts"
    echo "├── tools/       - Utility tools and generators"
    echo "├── systemd/     - System service files"
    echo "└── docs/        - Documentation and guides"
    echo ""
    echo -e "${BLUE}Quick Commands:${NC}"
    echo "  ./index.sh q   - Quick setup"
    echo "  ./index.sh r   - Run PoolMind"
    echo "  ./index.sh d   - Demo mode"
    echo "  ./index.sh s   - System status"
    echo ""
    echo -e "${BLUE}More Information:${NC}"
    echo "  README.md                    - Complete overview"
    echo "  docs/QUICKSTART.md          - Getting started guide"
    echo "  <category>/README.md        - Category-specific documentation"
}

install_services() {
    echo -e "${GREEN}${ICON_SYSTEMD} Installing Systemd Services${NC}"
    echo "This will copy service files to /etc/systemd/system/"
    echo ""

    if [[ $EUID -eq 0 ]]; then
        echo -e "${RED}Please run this as a regular user (not root)${NC}"
        return 1
    fi

    echo "Services to install:"
    echo "  - poolmind.service"
    echo "  - poolmind-update.service"
    echo "  - poolmind-update.timer"
    echo ""

    read -p "Continue with installation? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo cp systemd/*.service systemd/*.timer /etc/systemd/system/
        sudo systemctl daemon-reload
        echo -e "${GREEN}Services installed successfully!${NC}"
        echo ""
        echo "To enable and start:"
        echo "  sudo systemctl enable poolmind.service"
        echo "  sudo systemctl start poolmind.service"
    fi
}

check_service_status() {
    echo -e "${GREEN}${ICON_SYSTEMD} Service Status${NC}"
    echo ""

    services=("poolmind" "poolmind-update")
    timers=("poolmind-update")

    for service in "${services[@]}"; do
        echo -e "${BLUE}Service: ${service}${NC}"
        if systemctl is-active --quiet "$service"; then
            echo -e "  Status: ${GREEN}Active${NC}"
        elif systemctl is-enabled --quiet "$service" 2>/dev/null; then
            echo -e "  Status: ${YELLOW}Enabled but not running${NC}"
        else
            echo -e "  Status: ${RED}Not installed/enabled${NC}"
        fi
        echo ""
    done

    for timer in "${timers[@]}"; do
        echo -e "${BLUE}Timer: ${timer}${NC}"
        if systemctl is-active --quiet "${timer}.timer"; then
            echo -e "  Status: ${GREEN}Active${NC}"
            echo "  Next run: $(systemctl show "${timer}.timer" --property=NextElapseUSecRealtime --value | date -d @$(($(cat)/1000000)) 2>/dev/null || echo "Unknown")"
        else
            echo -e "  Status: ${RED}Not active${NC}"
        fi
        echo ""
    done
}

handle_menu_choice() {
    local menu=$1
    local choice=$2

    case $menu in
        "main")
            case $choice in
                1) clear; show_header; show_setup_menu; current_menu="setup" ;;
                2) clear; show_header; show_deployment_menu; current_menu="deployment" ;;
                3) clear; show_header; show_demo_menu; current_menu="demo" ;;
                4) clear; show_header; show_testing_menu; current_menu="testing" ;;
                5) clear; show_header; show_tools_menu; current_menu="tools" ;;
                6) clear; show_header; show_systemd_menu; current_menu="systemd" ;;
                7) clear; show_header; show_docs_menu; current_menu="docs" ;;
                q) quick_setup; read -p "Press Enter to continue..."; clear; show_header; show_menu ;;
                r) quick_run; read -p "Press Enter to continue..."; clear; show_header; show_menu ;;
                d) quick_demo; read -p "Press Enter to continue..."; clear; show_header; show_menu ;;
                s) quick_status; read -p "Press Enter to continue..."; clear; show_header; show_menu ;;
                h) clear; show_header; show_help; read -p "Press Enter to continue..."; clear; show_header; show_menu ;;
                x) echo -e "${GREEN}Goodbye!${NC}"; exit 0 ;;
                *) echo -e "${RED}Invalid choice${NC}"; sleep 1 ;;
            esac
            ;;
        "setup")
            case $choice in
                1) run_script "setup" "setup" ".sh"; read -p "Press Enter to continue..." ;;
                2) run_script "setup" "setup-pi" ".sh"; read -p "Press Enter to continue..." ;;
                3) run_script "setup" "run" ".sh"; read -p "Press Enter to continue..." ;;
                b) clear; show_header; show_menu; current_menu="main" ;;
                *) echo -e "${RED}Invalid choice${NC}"; sleep 1 ;;
            esac
            ;;
        "deployment")
            case $choice in
                1) run_script "deployment" "update" ".sh"; read -p "Press Enter to continue..." ;;
                2) run_script "deployment" "auto-update" ".sh"; read -p "Press Enter to continue..." ;;
                3) echo -n "Enter target host (e.g., pi@192.168.1.100): "; read target; run_script "deployment" "deploy-remote" ".sh" "$target"; read -p "Press Enter to continue..." ;;
                4) run_script "deployment" "status" ".sh"; read -p "Press Enter to continue..." ;;
                5) run_script "deployment" "validate-renovate" ".sh"; read -p "Press Enter to continue..." ;;
                b) clear; show_header; show_menu; current_menu="main" ;;
                *) echo -e "${RED}Invalid choice${NC}"; sleep 1 ;;
            esac
            ;;
        "demo")
            case $choice in
                1) run_script "demo" "demo" ".py"; read -p "Press Enter to continue..." ;;
                2) run_script "demo" "simple_demo" ".py"; read -p "Press Enter to continue..." ;;
                3) run_script "demo" "virtual_table" ".py"; read -p "Press Enter to continue..." ;;
                4) run_script "demo" "full_simulation" ".py"; read -p "Press Enter to continue..." ;;
                b) clear; show_header; show_menu; current_menu="main" ;;
                *) echo -e "${RED}Invalid choice${NC}"; sleep 1 ;;
            esac
            ;;
        "testing")
            case $choice in
                1) run_script "testing" "debug_aruco" ".py"; read -p "Press Enter to continue..." ;;
                2) run_script "testing" "debug_markers" ".py"; read -p "Press Enter to continue..." ;;
                3) run_script "testing" "test_aruco" ".py"; read -p "Press Enter to continue..." ;;
                4) run_script "testing" "test_pure_aruco" ".py"; read -p "Press Enter to continue..." ;;
                5) run_script "testing" "simple_aruco_test" ".py"; read -p "Press Enter to continue..." ;;
                b) clear; show_header; show_menu; current_menu="main" ;;
                *) echo -e "${RED}Invalid choice${NC}"; sleep 1 ;;
            esac
            ;;
        "tools")
            case $choice in
                1) run_script "tools" "gen_markers" ".py"; read -p "Press Enter to continue..." ;;
                2) run_script "tools" "camera_test" ".py"; read -p "Press Enter to continue..." ;;
                3) echo -n "Enter frame file path: "; read frame_path; run_script "tools" "inspect_frame" ".py" "$frame_path"; read -p "Press Enter to continue..." ;;
                b) clear; show_header; show_menu; current_menu="main" ;;
                *) echo -e "${RED}Invalid choice${NC}"; sleep 1 ;;
            esac
            ;;
        "systemd")
            case $choice in
                1) echo -e "${BLUE}Viewing poolmind.service:${NC}"; cat systemd/poolmind.service; read -p "Press Enter to continue..." ;;
                2) echo -e "${BLUE}Viewing poolmind-update.service:${NC}"; cat systemd/poolmind-update.service; read -p "Press Enter to continue..." ;;
                3) echo -e "${BLUE}Viewing poolmind-update.timer:${NC}"; cat systemd/poolmind-update.timer; read -p "Press Enter to continue..." ;;
                4) install_services; read -p "Press Enter to continue..." ;;
                5) check_service_status; read -p "Press Enter to continue..." ;;
                b) clear; show_header; show_menu; current_menu="main" ;;
                *) echo -e "${RED}Invalid choice${NC}"; sleep 1 ;;
            esac
            ;;
        "docs")
            case $choice in
                1) ${PAGER:-less} README.md; clear; show_header; show_docs_menu ;;
                2) ${PAGER:-less} docs/QUICKSTART.md; clear; show_header; show_docs_menu ;;
                3) ${PAGER:-less} docs/SIMULATION.md; clear; show_header; show_docs_menu ;;
                4) if command -v open >/dev/null; then open docs/; elif command -v xdg-open >/dev/null; then xdg-open docs/; else echo "Documentation in docs/ directory"; fi; read -p "Press Enter to continue..." ;;
                b) clear; show_header; show_menu; current_menu="main" ;;
                *) echo -e "${RED}Invalid choice${NC}"; sleep 1 ;;
            esac
            ;;
    esac
}

main() {
    # Handle command line arguments
    if [[ $# -gt 0 ]]; then
        case $1 in
            q) quick_setup; exit 0 ;;
            r) quick_run; exit 0 ;;
            d) quick_demo; exit 0 ;;
            s) quick_status; exit 0 ;;
            h|--help) show_help; exit 0 ;;
            *) echo -e "${RED}Unknown command: $1${NC}"; show_help; exit 1 ;;
        esac
    fi

    # Interactive mode
    current_menu="main"

    clear
    show_header
    show_menu

    while true; do
        echo -n -e "${GREEN}Choice: ${NC}"
        read -n 1 choice
        echo

        case $current_menu in
            "main") handle_menu_choice "main" "$choice" ;;
            "setup") handle_menu_choice "setup" "$choice"; if [[ "$choice" != "b" ]]; then show_setup_menu; fi ;;
            "deployment") handle_menu_choice "deployment" "$choice"; if [[ "$choice" != "b" ]]; then show_deployment_menu; fi ;;
            "demo") handle_menu_choice "demo" "$choice"; if [[ "$choice" != "b" ]]; then show_demo_menu; fi ;;
            "testing") handle_menu_choice "testing" "$choice"; if [[ "$choice" != "b" ]]; then show_testing_menu; fi ;;
            "tools") handle_menu_choice "tools" "$choice"; if [[ "$choice" != "b" ]]; then show_tools_menu; fi ;;
            "systemd") handle_menu_choice "systemd" "$choice"; if [[ "$choice" != "b" ]]; then show_systemd_menu; fi ;;
            "docs") handle_menu_choice "docs" "$choice"; if [[ "$choice" != "b" ]]; then show_docs_menu; fi ;;
        esac
    done
}

main "$@"
